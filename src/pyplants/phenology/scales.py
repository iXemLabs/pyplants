from datetime import datetime
from dataclasses import dataclass


@dataclass
class BBCHStage:
    """A single BBCH stage.

    Store separately vegetative and reproductive stage since they can overlap.
    """
    vstage: int
    rstage: int
    dt: datetime

    @property
    def stage(self):
        """Get the stage as an integer.

        :returns: the higher value between vegetative and reproductive
        """
        _vstage = 0 if self.vstage is None else self.vstage
        _rstage = 0 if self.rstage is None else self.rstage
        return max(_vstage, _rstage)

    def __eq__(self, other):
        if isinstance(other, BBCHStage):
            return self.vstage == other.vstage and self.rstage == other.rstage
        if isinstance(other, int):
            return self.stage == other
        raise TypeError("== supported only with int and BBCHStage")

    def __lt__(self, other):
        if isinstance(other, BBCHStage):
            return self.stage < other.stage
        if isinstance(other, int):
            return self.stage < other
        raise TypeError("< supported only with int and BBCHStage")

    def __le__(self, other):
        if isinstance(other, BBCHStage):
            return self.stage <= other.stage
        if isinstance(other, int):
            return self.stage <= other
        raise TypeError("<= supported only with int and BBCHStage")

    def __gt__(self, other):
        if isinstance(other, BBCHStage):
            return self.stage > other.stage
        if isinstance(other, int):
            return self.stage > other
        raise TypeError("> supported only with int and BBCHStage")

    def __ge__(self, other):
        if isinstance(other, BBCHStage):
            return self.stage >= other.stage
        if isinstance(other, int):
            return self.stage >= other
        raise TypeError(">= supported only with int and BBCHStage")


class BBCHScale(object):
    """BBCH scale used to track phenology stages.

    This scale is simply implemented as a list of :class:`.BBCHStage`.
    """

    def __init__(self):
        """Initialize an empty bbch scale."""
        self._scale = []

    def _is_empty(self):
        """Check if scale is empty.

        :returns: True if empty False otherwise
        """
        return len(self._scale) == 0

    @property
    def current_stage(self):
        """The current BBCH stage (0 not started)."""
        if len(self._scale) == 0:
            return BBCHStage(0, 0, None)
        return self._scale[-1]

    def add_stage(self, dt, v=None, r=None):
        """Add a new stage to the bbch scale.

        When reproductive stage is not yet reached it can be left empty.
        If reproductive stage was already reached, leaving it empty would rise
        a ValueError.
        The vegetative stage could be left empty only after reaching stage 9.

        :param dt: datetime object when stage is reached
        :param v: bbch vegetiva stage reached
        :param r: bbch reproductive stage reached
        """
        if len(self._scale) > 0:
            pstage = self._scale[-1]
            prev_v = pstage.vstage
            prev_r = pstage.rstage
            prev_t = pstage.dt
        else:
            prev_v = 0
            prev_r = None
            prev_t = None
        # Empy vegetative value is acceptable only if we already reached the 9.
        # Furhter value on this scale could be considered optionals.
        if v is None and prev_v < 9:
            raise ValueError("Missing value on vegetative scale")
        # After reproductive stage has strted r value can not be empty
        if r is None and prev_r is not None:
            raise ValueError("Missing mandatory value on reproductive scale")
        # Check the sequence of time to be respected
        if prev_t is not None and dt <= prev_t:
            raise ValueError("Invalid date provided")
        # Check the sequence of vegetative and reproductive to be ok
        if v is not None and v < prev_v:
            raise ValueError("Vegetative scale can not decrese")
        if r is not None and prev_r is not None and r < prev_r:
            raise ValueError("Reproductive scale can not decrese")
        # Finally we can add a new entry to the scale
        self._scale.append(BBCHStage(v, r, dt))

    def __iter__(self):
        """Make the BBCH scale iterable.

        :returns: an iterator to iterate over the scale
        """
        return iter(self._scale)

    def __repr__(self):
        """Friendly print the scale on repl."""
        n = len(self._scale)
        # Nothing to show with empty scale
        if n == 0:
            return "Empty scale [ ]"
        # Convert vegetative in string
        if self._scale[-1].vstage is None:
            v = "-"
        else:
            v = str(self._scale[-1].vstage)
        # Convert reproductive in string
        if self._scale[-1].rstage is None:
            r = "-"
        else:
            r = str(self._scale[-1].rstage)
        return "BBCH Scale [%d items]: Veg: %s; Rep: %s (last update: %s)" % (
            n, v, r, self._scale[-1].dt.strftime("%c"))
