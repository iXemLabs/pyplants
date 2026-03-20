from math import exp
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UpdateCtx:
    """Update context.

    Contains data used by models to run the update.
    """
    dt: datetime
    # Leaf wetness
    lw: int = None
    # Temperature
    tmean: float = None
    tmax: float = None
    tmin: float = None
    # Relative humidity
    rhmean: float = None
    rhmax: float = None
    rhmin: float = None
    # Rainfall
    rain: int = None
    # Timestep in use (hourly, daily)
    step: str = "h"

    @property
    def vpd_h(self):
        """The vapour pressure deficit.

        :raise AttributeError: in case t or rh is not defined
        """
        if self.tmean is None:
            raise AttributeError("Context is missing temperature")
        if self.rhmean is None:
            raise AttributeError("Context is missing relative humidity")
        return vpd_h(self.tmean, self.rhmean)


class LeafWetnessCounter(object):
    """Leaf wetness counter.

    Used to count continuous leaf wetness durations. After an update, the
    counter is automatically reset to zero as soon as a dry hour is met.

    This behavior can be changed by using the dry_off parameter. When provided
    the counter reset after dry_off consecutive hours.
    """

    def __init__(self, dry_off=1):
        """Init the leaf wetness duration.

        :param dry_off: number of consecutive dry hours
        """
        self._leaf_wd = 0
        self._dry_off = dry_off
        self._dry_period = 0

    @property
    def value(self):
        """Read the current leaf wetness duration."""
        return self._leaf_wd

    def update(self, lw: int):
        """Update the leaf wetness counter.

        :param lw: the current leaf wetness status
        """
        if lw == 1:
            self._leaf_wd += 1
            self._dry_period = 0
        else:
            # Check for interruption of a wetness period
            if self._leaf_wd > 0:
                self._dry_period += 1
                # Check the current dry period to be less then dry off
                if self._dry_period < self._dry_off:
                    self._leaf_wd += 1
                else:
                    self._leaf_wd = 0
                    self._dry_period = 0


def vpd_h(t, rh):
    """Compute the hourly vapour pressure deficit.

    :param t: hour mean temperature
    :param rh: hour mean relative humidity
    :returns: hourly vpd value
    """
    return (1 - (rh / 100)) * 6.11 * (exp((17.47 * t) / (239 + t)))
