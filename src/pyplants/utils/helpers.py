from typing import List
from typing import Tuple
from typing import Optional
from datetime import datetime

from pyplants.core.context import UpdateCtx


class LeafWetnessCounter(object):
    """Leaf wetness counter.

    Used to count continuous leaf wetness durations. After an update, the
    counter is automatically reset to zero as soon as a dry hour is met.

    This behavior can be changed by using the dry_off parameter. When provided
    the counter reset after dry_off consecutive hours.
    """

    def __init__(self, dry_off=1):
        """Init the leaf wetness duration.

        :param dry_off: number of consecutive dry hours
        """
        self._leaf_wd = 0
        self._dry_off = dry_off
        self._dry_period = 0

    @property
    def value(self):
        """Read the current leaf wetness duration."""
        return self._leaf_wd

    def update(self, lw: int):
        """Update the leaf wetness counter.

        :param lw: the current leaf wetness status
        """
        if lw == 1:
            self._leaf_wd += 1
            self._dry_period = 0
        else:
            # Check for interruption of a wetness period
            if self._leaf_wd > 0:
                self._dry_period += 1
                # Check the current dry period to be less then dry off
                if self._dry_period < self._dry_off:
                    self._leaf_wd += 1
                else:
                    self._leaf_wd = 0
                    self._dry_period = 0


class DailyUpdater(object):
    """Helper used to update daily models with hourly data.

    You can use this class to automatically update multiple modules with a
    daily timestep using hourly data. Since this helper performs a simple check
    over the dates to identify day progressions, it is mandatory to manually
    call the finalize method in order to correctly compute also the last date.
    """

    def __init__(self, models: List):
        """Init the daily updater.

        :param models: a list of models with daily timestep
        """
        self._models = models
        self._daily_ctx = None
        self._nsamples = 0

    def update(self, update_ctx: UpdateCtx):
        """Process an hourly update context.

        :param update_ctx: an hourly update context
        """
        if update_ctx.step != "h":
            raise ValueError("Please provide an hourly update context")
        # Lazy initialize the daily context
        if self._daily_ctx is None:
            self.__init_daily_context(update_ctx.dt)
        # When context has a different date we should trigger models update
        if update_ctx.dt.date() != self._daily_ctx.dt.date():
            self.__daily_update()
            self.__init_daily_context(update_ctx.dt)
        # Update the daily context with hourly data
        # (this implementation should be improved with an actual strategy pattern)
        # Leaf wetness
        self._daily_ctx.lw = self.__update_field(
            self._daily_ctx.lw, update_ctx.lw, strategy="acc")
        # Rainfalls
        self._daily_ctx.rain = self.__update_field(
            self._daily_ctx.rain, update_ctx.rain, strategy="acc")
        # First compute the tmin, tmax and tmean to be used to update the daily context
        tmin, tmax, tmean = DailyUpdater.__get_min_max_mean(
            update_ctx.tmin,
            update_ctx.tmax,
            update_ctx.tmean)
        # Update the temperature related fields
        self._daily_ctx.tmean = self.__update_field(
            self._daily_ctx.tmean, tmean)
        self._daily_ctx.tmax = self.__update_field(
            self._daily_ctx.tmax, tmax, strategy="max")
        self._daily_ctx.tmin = self.__update_field(
            self._daily_ctx.tmin, tmin, strategy="min")
        # First compute the rhmin, rhmax, rhmean to be used to update the daily context
        rhmin, rhmax, rhmean = DailyUpdater.__get_min_max_mean(
            update_ctx.rhmin,
            update_ctx.rhmax,
            update_ctx.rhmean)
        # Update the relative humidity related fields
        self._daily_ctx.rhmean = self.__update_field(
            self._daily_ctx.rhmean, rhmean)
        self._daily_ctx.rhmax = self.__update_field(
            self._daily_ctx.rhmax, rhmax, strategy="max")
        self._daily_ctx.rhmin = self.__update_field(
            self._daily_ctx.rhmin, rhmin, strategy="min")
        self._nsamples += 1

    def finalize(self):
        """Finalize the update."""
        if self._nsamples > 0:
            self.__daily_update()

    def __daily_update(self):
        """Update the models with internally computed context."""
        for model in self._models:
            model.update(self._daily_ctx)

    def __init_daily_context(self, dt: datetime):
        """Initialize a new daily update context.

        :param dt: the new datetime for the context
        """
        self._daily_ctx = UpdateCtx(dt=dt, step="d")
        self._nsamples = 0

    def __update_field(self, prev_value, value, strategy="mean"):
        """Compute next value for a field.

        :raise ValueError: on an unrecognized strategy provided
        :param prev_value: the previous value stored in the daily context
        :param value: the new provided value
        :param strategy: can be "mean", "max", "min", "acc"
        :returns: the next value to store in the daily context
        """
        if value is None:
            return prev_value
        if prev_value is None:
            return value
        next_val = None
        # Check the strategy and compute next value
        if strategy == "mean":
            next_val = (value + (self._nsamples * prev_value)) / (self._nsamples + 1)
        elif strategy == "max":
            next_val = max(prev_value, value)
        elif strategy == "min":
            next_val = min(value, prev_value)
        elif strategy == "acc":
            next_val = prev_value + value
        else:
            raise ValueError("Unknown update strategy provided")
        return next_val

    @staticmethod
    def __get_min_max_mean(
        vmin: Optional[float],
        vmax: Optional[float],
        vmean: Optional[float]
    ) -> Tuple[float, float, float]:
        """Get the min, max and mean for the provided optional values.

        Parameters such as temperature and realtive humidity could miss
        min and max measures in hourly sampling. In this case we select the
        mean value.

        :param vmin: the minimum value
        :param vmax: the maximum value
        :param vmean: the mean value
        :returns: a tuple containing the min, max and mean to be used
        """
        _vmax = vmean if vmax is None else vmax
        _vmin = vmean if vmin is None else vmin
        return _vmin, _vmax, vmean
