from enum import auto
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

from pyplants.utils import vpd_h


class CtxField(Enum):
    """Enum representing a possible field inside the update context."""
    LW = auto()
    TMAX = auto()
    TMIN = auto()
    TMEAN = auto()
    RHMAX = auto()
    RHMIN = auto()
    RHMEAN = auto()
    RAIN = auto()


@dataclass
class UpdateCtx:
    """The update context.

    A container for data used by models passed as input to the update method.
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
