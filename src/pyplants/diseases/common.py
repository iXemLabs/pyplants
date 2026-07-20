from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional
from typing import Callable
from datetime import datetime
from dataclasses import field
from dataclasses import dataclass

from pyplants.core.context import UpdateCtx
from pyplants.utils.helpers import LeafWetnessCounter


@dataclass(frozen=True)
class DiseaseEvent:
    """Generic model output container.

    Please note that spore release and infection are always reported as float.
    If a model output a boolean value the 0.0 and 1.0 values will be used.

    :param dt: datatime for this event
    :param spore_release: spore release (0...1)
    :param infection: infection risk (0...1)
    :param extra_field: dict with additional field based on model
    """
    dt: datetime
    spore_release: Optional[float] = None
    infection: Optional[float] = None
    # Additional field based on model internal logic
    extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        """Disease event to standard python dict.

        Provides additional benefits over using the `asdict` function since
        the `extra_fields` are flattened in the resulting dictionary.

        :returns: the disease event transformed as a dict
        """
        return {
            "dt": self.dt,
            "infection": self.infection,
            "spore_release": self.spore_release,
            **self.extra_fields
        }

    def __str__(self):
        s = []
        s.append("[%s]:" % self.dt.strftime("%c"))
        if self.spore_release is not None:
            s.append("spore release %.2f" % self.spore_release)
        if self.infection is not None:
            s.append("infection %.2f" % self.infection)
        return " ".join(s)


class InfectionManager(object):
    """A simple infection manager.

    This class is intended to be used by models to keep track of
    primary infections. An infection is described by two dates: start and end,
    of incubation and a latency parameter that describe the progression.

    The infection manager is model agnostic, in order to update the incubation
    latency an externally provided callable implementing the update strategy
    must be provided.
    """

    def __init__(self, fn_update_lat: Callable[[UpdateCtx], float]):
        """Initialize the infection manager.

        :param fn_update_lat: callable used to update incubation latency
        """
        self._infections = []
        self._fn_update_lat = fn_update_lat

    @property
    def infections(self) -> List[Dict]:
        """Get all the infections.

        :returns: the list of primary infections
        """
        return self._infections

    def add_infection(self, start: datetime):
        """Add a new infection.

        :param start: datetime of infection onset
        """
        self._infections.append({"start": start, "end": False, "latency": 0})

    def update(self, update_ctx: UpdateCtx):
        """Update all the running infections.

        :param update_ctx: update context with proper values
        """
        for infection in self._infections:
            if not infection["end"]:
                # Update incubation latency using model provided formula
                infection["latency"] += self._fn_update_lat(update_ctx)
                # Close infection when latency expires
                if infection["latency"] >= 1:
                    infection["end"] = update_ctx.dt


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
