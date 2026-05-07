from typing import Set
from typing import Dict
from typing import List
from collections import deque

from pyplants.core.base import BaseDiseaseWithPhenology
from pyplants.core.context import UpdateCtx
from pyplants.utils import gd_sum
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.common import DiseaseEvent
from pyplants.diseases.common import InfectionManager


class Plasmo(BaseDiseaseWithPhenology):
    """Plasmo model.

    Use hourly temperature, rain and leaf wetness to compute:

    * infection risk as boolean

    This module also compute the incubation period when infection occurs.
    """
    START_BBCH = 5

    def __init__(self, phen_model):
        """Init the model.

        :param phen_model: a phenological model
        """
        super().__init__(phen_model, None)
        # Rain count on a moving window of 24h
        self._raind = deque(maxlen=24)
        # Mean temperature during leaf wetness period
        self._tmeans = []
        # Leaf wetness counter
        self._leaf_wd = LeafWetnessCounter()
        # The infection manager to track primary infections
        self._inf_mng = InfectionManager(Plasmo.__compute_inf_latency)

    @property
    def infections(self) -> List[Dict]:
        """Detected infections with progression."""
        return self._inf_mng.infections

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with new data
        """
        if self._phen_model.scale.has_started(Plasmo.START_BBCH):
            inf = 0
            # Update rain and leaf wetness counter
            self._raind.append(update_ctx.rain)
            self._leaf_wd.update(update_ctx.lw)
            # Check to be in a leaf wetness period
            if self._leaf_wd.value > 0:
                self._tmeans.append(update_ctx.tmean)
                # Check infection condition
                raind = sum(self._raind)
                tmean = sum(self._tmeans) / len(self._tmeans)
                if raind > 8 and tmean >= 6 and tmean <= 26:
                    C_tw = gd_sum(self._tmeans)
                    f1 = 75.69 / C_tw
                    f2 = 1 / f1
                    if f2 >= 1:
                        inf = 1
                        self._inf_mng.add_infection(update_ctx.dt)
            else:
                self._tmeans.clear()
            # Create a disease event with infection risk
            self._events.append(DiseaseEvent(dt=update_ctx.dt, infection=inf))
            # Update the possible infections
            self._inf_mng.update(update_ctx)

    @property
    def req_update_ctx_fields(self) -> Set[str]:
        """Model required update context fields."""
        return {"tmean", "rhmean", "rain", "lw"}

    @staticmethod
    def __compute_inf_latency(update_ctx: UpdateCtx) -> float:
        """Compute the infection latency progressive step.

        This method is intended to be used with the infection manager.

        :param update_ctx: the currenct update context
        """
        incp = 0
        # Temperature and relative humidity thresholds
        TMIN, TMAX = 10, 34
        RHMIN = 30
        # Current measures
        tmean = update_ctx.tmean
        rhmean = update_ctx.rhmean
        if tmean >= TMIN and tmean <= TMAX and rhmean > RHMIN:
            incp = ((4 * (tmean - TMIN) * (TMAX - tmean)) / (
                (TMAX - TMIN) ** 2)) * 0.097 * (rhmean - RHMIN)
        return incp
