from datetime import datetime
from dataclasses import dataclass


class BBCHStage(object):
    """A simple BBCH stage."""
    _VEG = "v"
    _REP = "r"
    _THRESHOLD = 49

    def __init__(self, code: int):
        """Init the stage.

        :raises ValueError: when an invalid BBCH code is provided
        """
        if code <= 0 or code >= 99:
            raise ValueError("BBCH stage code must be between 00 and 99")
        self._code = code

    @property
    def code(self) -> int:
        """The entire BBCH code."""
        return self._code

    @property
    def main_phase(self) -> str:
        """Main phase (vegetative or reproductive)."""
        if self._code < BBCHStage._THRESHOLD:
            return BBCHStage._VEG
        return BBCHStage._REP

    def is_vegetative(self):
        """Check if the BBCH stage is vegetative scale or not.

        :returns: True if the code is less then `code:_THRESHOLD`
        """
        return self._code < BBCHStage._THRESHOLD

    def __eq__(self, other):
        if isinstance(other, BBCHStage):
            return self.code == other.code
        if isinstance(other, int):
            return self.code == other
        raise TypeError("equality supports only int and BBCHStage")

    def __ne__(self, other):
        if isinstance(other, BBCHStage):
            return self.code != other.code
        if isinstance(other, int):
            return self.code != other
        raise TypeError("inequality supports only int and BBCHStage")

    def __lt__(self, other):
        other_stage = self.__before_compare_op(other)
        return self.code < other_stage.code

    def __le__(self, other):
        other_stage = self.__before_compare_op(other)
        return self.code <= other_stage.code

    def __gt__(self, other):
        other_stage = self.__before_compare_op(other)
        return self.code > other_stage.code

    def __ge__(self, other):
        other_stage = self.__before_compare_op(other)
        return self.code >= other_stage.code

    def __before_compare_op(self, other):
        other_stage = None
        if isinstance(other, BBCHStage):
            other_stage = other
        if isinstance(other, int):
            other_stage = BBCHStage(other)
        if other_stage is None:
            raise TypeError("Can compare only with int and BBCHStage")
        if self.main_phase != other_stage.main_phase:
            raise ValueError("Can not compare on different scales")
        return other_stage


@dataclass
class BBCHRecord:
    """A single phenology record."""
    stage: BBCHStage
    dt: datetime

    def __str__(self):
        return "%02d on %s" % (self.stage.code, self.dt.strftime("%c"))


class BBCHStageAlreadyReached(Exception):
    """Raise when try to append an already reached BBCH stage."""
    pass


class BBCHScale(object):
    """BBCH scale used to track phenology.

    A simple implementation composed by two lists of :class:`BBCHRecord`,
    one for the vegetative and one for the reproductive scale.
    """

    def __init__(self):
        """Initialize the vegetative and reproductive scale."""
        self._vscale = []
        self._rscale = []

    @property
    def vscale(self):
        """The vegetative scale."""
        return self._vscale

    @property
    def rscale(self):
        """The reproductive scale."""
        return self._rscale

    def add_stage(self, dt: datetime, code: int):
        """Add a new phenology stage to the proper scale.

        :param dt: datetime of the new stage
        :param code: the code of the new stage
        """
        stage = BBCHStage(code)
        # Select the proper scale
        scale = self._vscale if stage.is_vegetative() else self._rscale
        # Check progression rule (date and code)
        if len(scale) > 0:
            if scale[-1].dt >= dt:
                raise ValueError("Invalid temporal progression!")
            if scale[-1].stage >= stage:
                raise BBCHStageAlreadyReached
        # Progression require new stage to be appended
        scale.append(BBCHRecord(stage, dt))

    def has_started(self, code: int) -> bool:
        """Check if a given stage (code) has been reached.

        :param code: the code stage
        :returns: True if last code in the scale is less than equals code
        """
        stage = BBCHStage(code)
        # Select the proper scale
        scale = self._vscale if stage.is_vegetative() else self._rscale
        # Check the scale not to be empty and then compare
        if len(scale) > 0:
            return scale[-1].stage >= stage
        return False

    def has_ended(self, code: int) -> bool:
        """Check if a given stage (code) has been passed.

        :param code: the code stage
        :returns: True if last code in the scale is greather than code
        """
        stage = BBCHStage(code)
        # Select the proper scale
        scale = self._vscale if stage.is_vegetative() else self._rscale
        # Check the scale not to be empty and then compare
        if len(scale) > 0:
            return scale[-1].stage > stage
        return False
