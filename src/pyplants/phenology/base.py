from abc import ABC
from abc import abstractmethod
from datetime import datetime

from pyplants.utils import UpdateCtx
from pyplants.phenology.scales import BBCHScale


class BasePhenology(ABC):
    """Base class for phenological model using BBCH scale."""

    def __init__(self):
        self._bbch = BBCHScale()

    @property
    def current_stage(self):
        """The current stage reached.

        :returns: the most recent bbch stage
        """
        return self._bbch.current_stage

    @property
    def scale(self):
        """Get the BBCH scale."""
        return self._bbch

    @abstractmethod
    def update(self, dt: datetime, update_ctx: UpdateCtx):
        """Abstract method to update the model.

        :param dt: python datetime for provided sample
        :param update_ctx: update context for the implemented model
        """
        pass
