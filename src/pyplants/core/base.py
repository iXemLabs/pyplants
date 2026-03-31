from abc import ABC
from abc import abstractmethod
from typing import Set
from typing import List
from typing import Tuple

from pyplants.core.context import UpdateCtx
from pyplants.phenology.scales import BBCHScale
from pyplants.diseases.common import DiseaseEvent


class Model(ABC):
    """Base interface for models.

    Template models (e.g. disease and phenology) can implement the update
    method with custom logic. Each specific implementation of a concrete
    model, instead, should implement the private method _update_imp.
    """

    @abstractmethod
    def update(self, update_ctx: UpdateCtx):
        """Update the model using new data.

        :param update_ctx: the update context with weather data
        """
        pass

    @abstractmethod
    def _update_imp(self, update_ctx: UpdateCtx):
        """Abstract method to be implemented for each concrete model.

        :param update_ctx: the update context with weather data
        """
        pass


class BasePhenology(Model):
    """Base class for phenological model.

    By default tracks phenology using BBCH scale.
    """

    def __init__(self):
        """Init the base phenology model."""
        self._bbch = BBCHScale()

    @property
    def scale(self) -> BBCHScale:
        """Get the BBCH scale.

        :returns: the BBCH scale as list of BBCHStage
        """
        return self._bbch

    def update(self, update_ctx: UpdateCtx):
        """Simply call the concrete update implementation.

        :param update_ctx: the update context with weather data
        """
        self._update_imp(update_ctx)


class BaseDisease(Model):
    """Base class for disease model."""

    def __init__(self):
        """Init the base disease model"""
        self._events = []

    @property
    def events(self) -> List[DiseaseEvent]:
        """Get the events computed by the model.

        :returns: the list of events computed
        """
        return self._events

    @property
    @abstractmethod
    def req_update_ctx_fields(self) -> Set[str]:
        """Required update context fields.

        :returns: a set with mandatory fields
        """
        pass

    def update(self, update_ctx: UpdateCtx):
        """Update the model using the specific model implementation.

        :param update_ctx: update context with proper values
        """
        # Loop over the required update context fields
        for f in self.req_update_ctx_fields:
            if getattr(update_ctx, f) is None:
                raise ValueError("Update context missing: %s" % f)
        # Call the implemented model update
        self._update_imp(update_ctx)


class BaseDiseaseWithPhenology(BaseDisease):
    """Base class for disease models that requires phenology data."""

    def __init__(
        self, phen_model: BasePhenology, bbch_period: Tuple[int, int]
    ):
        """Initialize the model.

        :param phen_model: a phenology model to use
        :param bbch_period: bbch range in which the model should run
        """
        super().__init__()
        self._phen_model = phen_model
        self._bbch_period = bbch_period

    def update(self, update_ctx: UpdateCtx):
        """Update the model using the specific model implementation.

        Before calling the specific update implementation check the current
        BBCH value to be in range (if provided), otherwise skip the execution.

        :param update_ctx: update context with proper values
        """
        if self._bbch_period is not None:
            cstage = self._phen_model.scale.current_stage
            if cstage < self._bbch_period[0] or cstage > self._bbch_period[1]:
                return
        super().update(update_ctx)
