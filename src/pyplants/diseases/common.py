from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Callable
from datetime import datetime
from dataclasses import field
from dataclasses import dataclass

from pyplants.core.context import UpdateCtx


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

    def __str__(self):
        s = []
        s.append("[%s]: spore release %.2f" % (
            self.dt.strftime("%c"),
            self.spore_release
        ))
        if self.infection is not None:
            s.append("infection %.2f" % self.infection)
        return " ".join(s)


class InfectionManager(object):
    """A simple infection manager.

    This class is intended to be used by models to keep track of
    primary infections. An infection is described by two dates: start and end,
    and a latency parameter that describe the progression.

    The infection manager is model agnostic, in order to update the infection
    latency an externally provided callable implementing the update strategy
    must be provided.
    """

    def __init__(self, fn_update_lat: Callable[[UpdateCtx], float]):
        """Initialize the infection manager.

        :param fn_update_lat: callable used to update infection latency
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
                # Update latency for infection using model provided formula
                infection["latency"] += self._fn_update_lat(update_ctx)
                # Close infection when latency expires
                if infection["latency"] >= 1:
                    infection["end"] = update_ctx.dt
