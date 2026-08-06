from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from inspect import isabstract

from pyplants.core.context import UpdateCtx
from pyplants.phenology.scales import BBCHScale
from pyplants.diseases.common import DiseaseEvent


def _validate_model(metadata: Dict):
    """Validate a model blueprint.

    Models should define a configuration as a class attribute. If the concrete
    class does not define the configuration in the appropriate way an exception
    is raised.

    :param metadata: the configuration dictionary
    :raise KeyError: when a mandatory key is not defined in the configuration
    :raise ValueError: when a field is not defined in the proper way
    """
    missing_keys = []
    # Check for mandatory fields
    if "timestep" not in metadata:
        missing_keys.append("timestep")
    if "use_ctx_fields" not in metadata:
        missing_keys.append("use_ctx_fields")
    if len(missing_keys) != 0:
        raise KeyError("Invalid model: missing %s" % ",".join(missing_keys))
    # Check attributes validity
    if metadata["timestep"] != "d" and metadata["timestep"] != "h":
        raise ValueError("Timestep value can be only 'h' or 'd'")
    if not isinstance(metadata["use_ctx_fields"], set):
        raise ValueError("The use_ctx_fields must be a set")


class Model(ABC):
    """Base interface for models.

    Template models (e.g. disease and phenology) can override the update
    method, by adding additional custom logic. Each concrete implementations,
    instead, must implement the private method :code:`_update_imp`.
    """

    def __init_subclass__(cls, **kwargs):
        """Validate sub classes blueprint.

        :raise TypeError: when no configuration is defined
        :raise KeyError: when validation fails because of missing fields
        :raise ValueError: when validation fails because of malformed fields
        """
        super().__init_subclass__(**kwargs)
        # Abstract class does not need validation
        if isabstract(cls):
            return
        if not hasattr(cls, "_model_meta"):
            raise TypeError("A model must define a class attribute _model_meta")
        _validate_model(cls._model_meta)

    def update(self, update_ctx: UpdateCtx):
        """Update the model with fresh data.

        Internally use the concrete update implementation. Before calling the
        update, the following checks are performed:

        * timestep validity (as defined in _model_meta)
        * required fields to be not :code:`None`

        :param update_ctx: the update context with new data
        :raise ValueError: when an invalid update contex is provided
        """
        if update_ctx.step != self._model_meta["timestep"]:
            raise ValueError("Model and update context timestep mismatch")
        # Check required fields for the model
        for f in self._model_meta["use_ctx_fields"]:
            _f = f.name.lower()
            if getattr(update_ctx, _f) is None:
                raise ValueError("Update context missing: %s" % _f)
        self._update_imp(update_ctx)

    @abstractmethod
    def _update_imp(self, update_ctx: UpdateCtx):
        """Abstract method to be implemented for each concrete model.

        :param update_ctx: the update context with weather data
        """
        pass

    @classmethod
    def get_metadata(cls):
        """Get the model metadata.

        :returns: a copy of the model metadata dictionary
        """
        return cls._model_meta.copy()


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

    def _is_in_infection_period(self):
        """Check if we are currently in an infection period.

        An infection period is a contiguous period where infection is detected.

        :return: True if the last event was an infection
        """
        if len(self._events) == 0:
            return False
        return self._events[-1].infection > 0


class BaseDiseaseWithPhenology(BaseDisease):
    """Base class for disease models that requires phenology data."""

    def __init__(self, phen_model: BasePhenology):
        """Initialize the model.

        :param phen_model: a phenology model to use
        """
        super().__init__()
        self._phen_model = phen_model

    def update(self, update_ctx: UpdateCtx):
        """Update the model with fresh data.

        Internally use the concrete update implementation. Before calling the
        update, configuration is used to validate the update context fields.

        If provided in the model configuration, the update is invoked only when
        curreny phenology falls in the given bbch range.

        :param update_ctx: the update context with new data
        """
        if "bbch_range" in self._model_meta:
            bbch_range = self._model_meta["bbch_range"]
            if bbch_range[0] is not None:
                if not self._phen_model.scale.has_started(bbch_range[0]):
                    return
            if bbch_range[1] is not None:
                if self._phen_model.scale.has_ended(bbch_range[1]):
                    return
        super().update(update_ctx)
