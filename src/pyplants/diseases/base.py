from typing import Set
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Callable
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from dataclasses import field
from dataclasses import asdict
from dataclasses import dataclass

from pyplants.utils import UpdateCtx


class BaseDisease(ABC):
    """Base class for all disease model."""

    def __init__(self):
        """Init the base model."""
        self._events = []
        self._last_update = None

    @property
    def events(self):
        """Get the events computed by the model.

        :returns: the list of events computed
        """
        return self._events

    def update(self, dt: datetime, update_ctx: UpdateCtx):
        """Update the model using the specific model implementation.

        :param dt: update datetime object
        :param update_ctx: update context with proper values
        """
        update_args = asdict(update_ctx)
        # Loop over the required update context fields
        for f in self.update_ctx_fields:
            if update_args[f] is None:
                raise ValueError("Update context missing: %s" % f)
        # Call the implemented model update
        self._update_imp(dt, update_ctx)

    @property
    @abstractmethod
    def update_ctx_fields(self) -> Set[str]:
        pass

    @abstractmethod
    def _update_imp(self, dt: datetime, update_ctx: UpdateCtx):
        pass


class BaseDiseaseWithPhenology(BaseDisease):
    """Base class for disease models that requires phenology data."""

    def __init__(self, phen_model, bbch_period):
        """Initialize the model.

        :param phen_model: a phenology model to use
        :param bbch_period: bbch range in which the model should run
        :param phen_auto_update: if model has to automatically update phenology
        """
        super().__init__()
        self._phen_model = phen_model
        self._bbch_period = bbch_period
        self._phen_auto_update = False

    def update(self, dt: datetime, update_ctx: UpdateCtx):
        """Update the model using the specific model implementation.

        If phen_auto_update is set to True update als the phenology model.

        Before calling the specific update implementation check the current
        BBCH value to be in range (if provided), otherwise skip the execution.

        :param dt: update datetime object
        :param update_ctx: update context with proper values
        """
        if self._phen_auto_update:
            self._phen_model.update(dt, update_ctx)
        # Check phenology to be in range (if provided)
        if self._bbch_period is not None:
            cstage = self._phen_model.current_stage
            if cstage < self._bbch_period[0] or cstage > self._bbch_period[1]:
                return
        super().update(dt, update_ctx)


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

    def update(self, dt: datetime, update_ctx: UpdateCtx):
        """Update all the running infections.

        :param dt: datetime of the update context
        :param update_ctx: update context with proper values
        """
        for infection in self._infections:
            if not infection["end"]:
                # Update latency for infection using model provided formula
                infection["latency"] += self._fn_update_lat(update_ctx)
                # Close infection when latency expires
                if infection["latency"] >= 1:
                    infection["end"] = dt
