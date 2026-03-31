from math import exp
from typing import Set

from pyplants.core.base import BaseDiseaseWithPhenology
from pyplants.core.context import UpdateCtx
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.common import DiseaseEvent


class Broome(BaseDiseaseWithPhenology):
    """Broome GM model.

    Use hourly temperature and leaf wetness to compute:

    * infection risk

    This module compute infection risk during continuous leaf wetness periods
    counted using a dry_off equals to 4h.
    """
    START_BBCH = 65
    END_BBCH = 89

    def __init__(self, phen_model):
        """Init the model.

        :param phen_model: a grape phenological model
        """
        super().__init__(phen_model, (Broome.START_BBCH, Broome.END_BBCH))
        # A leaf wetness counter
        self._leaf_wd = LeafWetnessCounter(dry_off=4)

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with temperature and leaf wetness
        """
        inf = 0
        self._leaf_wd.update(update_ctx.lw)
        # Check to be in a leaf wetness period
        if self._leaf_wd.value > 0:
            t = update_ctx.tmean
            w = self._leaf_wd.value
            # Compute the Broome Index
            index = -2.647866 - (0.374927 * w) + (0.061601 * w * t) \
                - (0.001511 * w * (t ** 2))
            index = exp(index)
            inf = index / (1 + index)
        self._events.append(DiseaseEvent(dt=update_ctx.dt, infection=inf))

    @property
    def req_update_ctx_fields(self) -> Set[str]:
        """Model required update context fields."""
        return {"t", "lw"}
