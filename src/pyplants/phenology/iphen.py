import csv

from bisect import bisect_left
from importlib.resources import read_text

from pyplants.utils import UpdateCtx
from pyplants.utils.nhh import NHH, get_nhh_params
from pyplants.utils.plants import PlantEnum
from pyplants.phenology.base import BasePhenology


class Iphen(BasePhenology):
    """Iphen phenological model for grape, based on [1]_.

    Internally use the NHH (Normal Hour Heat) [2]_.
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

    def update(self, update_ctx: UpdateCtx):
        """Update the model using the mean hourly temperature.

        :param update_ctx: the update context object
        """
        self._nhh.update(update_ctx.t)
        # Computed next BBCH values
        bbch_v = 0
        bbch_r = 0
        # Current BBCH values
        cur_vstage = self._bbch.current_stage.vstage
        cur_rstage = self._bbch.current_stage.rstage
        # Check the vegetative scale not to be over
        max_bbch_v = self.__table_v["bbch"][-1]
        if cur_vstage < max_bbch_v:
            # Search inside the table current nhh
            pos = bisect_left(self.__table_v["nhh"], self._nhh.value)
            if pos > 0:
                bbch_v = self.__table_v["bbch"][pos - 1]
        else:
            # If no more vegetative stage stay on the last
            bbch_v = cur_vstage
        # Check the reproductive scale to be started
        if self._nhh.value >= self.__table_r["nhh"][0]:
            # And not to be over
            max_bbch_r = self.__table_r["bbch"][-1]
            if cur_rstage < max_bbch_r:
                bbch_r = self.__table_r["bbch"][0]
                # Search inside the table current nhh
                pos = bisect_left(self.__table_r["nhh"], self._nhh.value)
                if pos > 0:
                    bbch_r = self.__table_r["bbch"][pos - 1]
            else:
                bbch_r = cur_rstage
        # Check if a new stage has been reached
        if (self._bbch.current_stage.vstage != bbch_v
                or self._bbch.current_stage.rstage != bbch_r):
            self._bbch.add_stage(update_ctx.dt, v=bbch_v, r=bbch_r)

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
            table[f].append(row[f])
    return table


_vegetative = __load_data("nhh_vegetative.csv")
_reproductive = __load_data("nhh_reproductive.csv")
