import csv

from bisect import bisect_left
from importlib.resources import read_text

from pyplants.utils.nhh import NHH, get_nhh_params
from pyplants.utils.plants import PlantEnum
from pyplants.core.base import BasePhenology
from pyplants.core.context import UpdateCtx
from pyplants.phenology.scales import BBCHStageAlreadyReached


class Iphen(BasePhenology):
    """Iphen phenological model for grape.

    Internally use the NHH (Normal Hour Heat).
    """

    def __init__(self, nhh_params, nhh_2_bbch_v, nhh_2_bbch_r):
        """Initialize the model.

        :param nhh_params: a tuple containing tcmin, tcopt and tcmax
        :param nhh_2_bbch_v: table to translate nnh to vegetative bbch
        :param nhh_2_bbch_r: table to translate nhh to reproductive bbch
        """
        super().__init__()
        # Create the NHH model using the min,max and opt params
        self._nhh = NHH(*nhh_params)
        # Store the provided lookup table for both scales
        self.__table_v = nhh_2_bbch_v
        self.__table_r = nhh_2_bbch_r

    def set_nhh_params(self, nhh_params):
        """Set NHH params.

        You can only change NHH params before starting the model.
        (i.e. before first call to the update method)

        :param nhh_params: a tuple containing tcmin, tcopt and tcmax
        :raise: RuntimeError
        """
        self._nhh.set_params(*nhh_params)

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model using the mean hourly temperature.

        :param update_ctx: the update context object
        """
        self._nhh.update(update_ctx.tmean)
        skip = False
        # Process the vegetative scale
        if len(self._bbch.vscale) > 0:
            cur_vstage = self._bbch.vscale[-1]
            max_bbch_v = self.__table_v["bbch"][-1]
            # Check the vegetative scale not to be over
            if cur_vstage.stage == max_bbch_v:
                skip = True
        # We search inside the table only if needed
        if not skip:
            pos = bisect_left(self.__table_v["nhh"], self._nhh.value)
            if pos > 0:
                code = self.__table_v["bbch"][pos - 1]
                try:
                    self._bbch.add_stage(update_ctx.dt, code)
                except BBCHStageAlreadyReached:
                    pass
        skip = False
        # Process the reproductive scale
        # If the scale is not started or over we can skip...
        if self._nhh.value >= self.__table_r["nhh"][0]:
            if len(self._bbch.rscale) > 0:
                cur_rstage = self._bbch.rscale[-1]
                max_bbch_r = self.__table_r["bbch"][-1]
                if cur_rstage.stage == max_bbch_r:
                    skip = True
        else:
            skip = True
        if not skip:
            pos = bisect_left(self.__table_r["nhh"], self._nhh.value)
            if pos > 0:
                code = self.__table_r["bbch"][pos - 1]
                try:
                    self._bbch.add_stage(update_ctx.dt, code)
                except BBCHStageAlreadyReached:
                    pass

    @classmethod
    def build_from_plant(cls, plant, variety):
        """Build a model using a specific plant type.

        For the moment only grape plant is supported for this model.

        :param plant: target plant enum type
        :param variety: plant variety string
        :returns: model instance configured
        :raises ValueError: on invalid plant or variety provided
        """
        if not isinstance(plant, PlantEnum):
            raise ValueError("Unknown plant provided in input")
        # Currently only the GRAPE is supported
        if plant != PlantEnum.GRAPE:
            raise NotImplementedError("Only GRAPE plant currently supported")
        # The supported variety can be controlled among the keys of the tables
        if variety not in _vegetative.keys():
            raise ValueError("Unknown variety provided")
        # Initialized the support tables for vegetative and reproductive scales
        table_v = {
            "bbch": _vegetative["BBCH"],
            "nhh": _vegetative[variety]
        }
        table_r = {
            "bbch": _reproductive["BBCH"],
            "nhh": _reproductive[variety]
        }
        return cls(get_nhh_params(plant), table_v, table_r)


def __load_data(fname):
    """Load the lookup table for this model.

    :param fname: the name of the file located in data folder
    :returns: a dict with bbch and nhh values for each plant
    """
    data = read_text("pyplants.data", fname).splitlines()
    reader = csv.DictReader(data, quoting=csv.QUOTE_NONNUMERIC)
    # Parse the file into a dict
    table = {}
    # Init the list for each field
    for f in reader.fieldnames:
        table[f] = []
    # Add samples for each row
    for row in reader:
        for f in reader.fieldnames:
            table[f].append(int(row[f]))
    return table


_vegetative = __load_data("nhh_vegetative.csv")
_reproductive = __load_data("nhh_reproductive.csv")
