from math import exp

from pyplants.core.base import BaseDiseaseWithPhenology
from pyplants.core.context import UpdateCtx
from pyplants.core.context import CtxField
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.common import DiseaseEvent
from pyplants.diseases.common import GenericMagarey


class Broome(BaseDiseaseWithPhenology):
    """Broome GM model.

    Use hourly temperature and leaf wetness to compute:

    * infection risk

    This module compute infection risk during continuous leaf wetness periods
    counted using a dry_off equals to 4h.
    """
    _model_meta = {
        "timestep": "h",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.LW},
        "bbch_range": (65, 89)
    }

    def __init__(self, phen_model):
        """Init the model.

        :param phen_model: a grape phenological model
        """
        super().__init__(phen_model)
        # A leaf wetness counter
        self._leaf_wd = LeafWetnessCounter(dry_off=4)
        # List of temperature during wet period
        self._tmeans = []

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with temperature and leaf wetness
        """
        inf = 0
        self._leaf_wd.update(update_ctx.lw)
        # Check to be in a leaf wetness period
        if self._leaf_wd.value > 0:
            # Accumulate the temperatures during wet period
            self._tmeans.append(update_ctx.tmean)
            # Compute the mean during wet period
            t = sum(self._tmeans) / len(self._tmeans)
            # Compute the Broome index using temperature and wetness hours
            w = self._leaf_wd.value
            index = -2.647866 - (0.374927 * w) + (0.061601 * w * t) \
                - (0.001511 * w * (t ** 2))
            index = exp(index)
            inf = index / (1 + index)
        else:
            self._tmeans.clear()
        self._events.append(DiseaseEvent(dt=update_ctx.dt, infection=inf))


class GoFe(BaseDiseaseWithPhenology):
    """González-Fernández risk periods model (GM).

    Use hourly temperature and leaf wetness to compute:

    * infection risk

    This model is based on the Magarey model and operate differently during
    flowering and ripening.
    """
    _model_meta = {
        "timestep": "h",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.LW}
    }

    def __init__(self, phen_model):
        """Init the model.

        :param phen_model: a grape phenological model
        """
        super().__init__(phen_model)
        # Flowering parameters
        self._magarey_flowering = GenericMagarey((1, 25, 34), 1, 12, 13)
        # Ripening parameters
        self._magarey_ripening = GenericMagarey((10, 20, 35), 4, 10, 13)

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with temperature and leaf wetness
        """
        infection = 0
        magarey_model = None
        if self._phen_model.scale.in_range(65, 68):
            magarey_model = self._magarey_flowering
        elif self._phen_model.scale.in_range(81, 89):
            magarey_model = self._magarey_ripening
        # Check if one of the two models has been selected
        if magarey_model is not None:
            magarey_model.update(update_ctx)
            infection = int(magarey_model.has_infection)
        self._events.append(DiseaseEvent(dt=update_ctx.dt, infection=infection))
