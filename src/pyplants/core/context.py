from datetime import datetime
from dataclasses import dataclass

from pyplants.utils import vpd_h


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
