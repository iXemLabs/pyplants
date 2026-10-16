from typing import Tuple

from pyplants.core.context import UpdateCtx
from pyplants.utils.helpers import LeafWetnessCounter


class GenericMagarey(object):
    """The generic Magarey model for fungine disease."""

    def __init__(self, tcard: Tuple[int, int, int], wmin: int, wmax: int, dry_off: int):
        """Initializes the Magarey generic fungal infection model.

        :param tcard: tuple with cardinal temperatures (min, opt, max) in °C
        :param wmin: minimum wetness duration required (hours)
        :param wmax: maximum wetness duration  for the infection process (hours)
        :param dry_off: maximum dry hour to merge wetness periods
        """
        self._tmin = tcard[0]
        self._topt = tcard[1]
        self._tmax = tcard[2]
        # Wetness duration params
        self._wmin = wmin
        self._wmax = wmax
        # Leaf wetness counter
        self._lwd = LeafWetnessCounter(dry_off=dry_off)
        self._tmean = []
        # Current infection state
        self._has_infection = False

    @property
    def has_infection(self):
        """If an infection has been spot since the last update."""
        return self._has_infection

    def update(self, update_ctx: UpdateCtx):
        """Update the model with new data.

        After the update, it is possible to check if an infection has been detected
        by checking the :code:`has_infection` property.

        :param update_ctx: the update context with data
        """
        inf = False
        self._lwd.update(update_ctx.lw)
        if self._lwd.value > 0:
            # Store tmean to compute mean during wetness period
            self._tmean.append(update_ctx.tmean)
            tmean = sum(self._tmean) / len(self._tmean)
            # Compute the hours of wetness to have in infection
            wt = self._get_wetness_required(tmean)
            inf = self._lwd.value >= wt
        else:
            self._tmean.clear()
        self._has_infection = inf

    def _yin_rfunc(self, tmean: float) -> float:
        """Compute the Yin temperature response function.

        :param tmean: mean temperature in an hour (°C)
        :returns: the temperature response using the cardinal temperatures
        """
        if tmean < self._tmin or tmean > self._tmax:
            return 0
        delta_max_opt = self._tmax - self._topt
        delta_opt_min = self._topt - self._tmin
        # Compute the two part of the function
        p1 = (self._tmax - tmean) / (delta_max_opt)
        p2 = (tmean - self._tmin) / (delta_opt_min)
        return p1 * (p2 ** (delta_opt_min / delta_max_opt))

    def _get_wetness_required(self, tmean: float):
        """Compute the required wetness duration for an infection.

        :param tmean: mean temperature in an hour (°C)
        :returns: number of hours of wetness for infection
        """
        wt = None
        ft = self._yin_rfunc(tmean)
        # In case of zero (tmena out of bound) we return wmax
        if ft == 0:
            wt = self._wmax
        else:
            # Bound wetness duration to wmax
            wt = min(self._wmin / ft, self._wmax)
        return wt
