import csv

from math import exp
from math import isclose
from typing import Dict
from typing import List
from bisect import bisect_right
from importlib.resources import read_text

from pyplants.core.base import BaseDisease
from pyplants.core.base import BaseDiseaseWithPhenology
from pyplants.core.context import UpdateCtx
from pyplants.core.context import CtxField
from pyplants.utils import kdbeta
from pyplants.utils import equiv_temp
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.common import DiseaseEvent
from pyplants.diseases.common import InfectionManager


class Gadoury(BaseDiseaseWithPhenology):
    """Gadoury PM model.

    Use daily temperature and rain data to compute:

    - ascospore release event
    - infection event

    Please note that this is a simple empirical model, and it produces
    boolean value for putative events.
    """
    _model_meta = {
        "timestep": "d",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.RAIN},
        "bbch_range": (9, 68)
    }

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with daily data.

        :param update_ctx: update context with temperature and rain
        """
        t = update_ctx.tmean
        r = update_ctx.rain
        # Check expert rules
        dis = r >= 2.5 and t >= 4 and t <= 27
        inf = dis and t >= 10
        # Store the event and convert bool to float for compatibility
        self._events.append(DiseaseEvent(
            dt=update_ctx.dt,
            spore_release=float(dis),
            infection=float(inf)
        ))


class Moyer(BaseDisease):
    """Moyer ascospore release model.

    Use daily max temperature and cumulative rain to compute:

    - ascospore release event (boolean)

    The ascospore discharge period is an internal parameter used to compute the
    time period in which the model has to run. It stops when 100% is reached.
    """
    _model_meta = {
        "timestep": "d",
        "use_ctx_fields": {CtxField.TMAX, CtxField.RAIN}
    }

    def __init__(self):
        """Initialize the model."""
        super().__init__()
        # Ascospore discharge events count
        self._n_dis = 0
        # Degree-day with zero base
        self._dd = 0
        # Last computed ascospore period
        self._asc_p = 0

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with daily data.

        :param update_ctx: update context with max temperature and rain
        """
        if not isclose(self._asc_p, 1):
            r = update_ctx.rain
            tmax = update_ctx.tmax
            # Ascospore release rule
            dis = r >= 2.5 and tmax > 0
            # Count the discharge event if any
            self._n_dis += int(dis)
            # Update the ascospore release period
            if tmax > 0:
                self._dd += tmax
                # Compute asc release period
                a = 0.00222 * self._dd
                b = 0.150287 * self._n_dis
                self._asc_p = 1 - exp(-exp(-3.335 + a + b))
            # Create the disease event and add asc_p as additional field
            self._events.append(DiseaseEvent(
                dt=update_ctx.dt,
                spore_release=float(dis),
                extra_fields={"asc_p": self._asc_p}
            ))


class _MillsPM(object):
    """Mills table for PM prediction.

    Singleton private implementation not to be directly used.
    """
    _instance = None

    def __new__(cls):
        """Constructor with singleton implementation."""
        if cls._instance is None:
            cls._instance = super(_MillsPM, cls).__new__(cls)
            # Initialize the look up table only once
            data = read_text("pyplants.data", "mills_pm.csv").splitlines()
            reader = csv.reader(data, quoting=csv.QUOTE_NONNUMERIC)
            # Store the wetness duration levels
            columns = next(reader)
            cls._instance._wet_durations = columns[1:]
            # Store the risk level tables
            cls._instance._table = []
            for row in reader:
                cls._instance._table.append({
                    "t": row[0],
                    "risks": [int(risk) for risk in row[1:]]
                })
        return cls._instance

    def get_risk(self, t, lwd):
        """Get the risk associated to provided values.

        :param t: mean hourly temperature
        :param lwd: consecutive leaf wetness duration (hours)
        :returns: risk level (0,1,2,3)
        """
        if lwd >= self._wet_durations[0]:
            # Check the temperature to be in range of mills table
            min_t = self._table[0]["t"]
            max_t = self._table[-1]["t"]
            if t >= min_t and t <= max_t:
                # Get the nearest absolute temperature
                row = min(self._table, key=lambda x: abs(x["t"] - t))
                # Search inside the wetness durations
                pos = bisect_right(self._wet_durations, lwd)
                return row["risks"][pos - 1]
        return 0


class DavisRI(BaseDiseaseWithPhenology):
    """Davis Risk Index model.

    Use hourly temperature and leaf wetness to compute:

    - ascospore relese event

    This model uses a modified Mills table to compute the risk level
    expressed as: no risk, low, medium, high (0, 1, 2, 3).
    """
    _model_meta = {
        "timestep": "h",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.LW},
        "bbch_range": (9, 75)
    }

    def __init__(self, phen_model):
        """Initialize the model.

        :param phen_model: a grape phenological model
        """
        super().__init__(phen_model)
        # List of hourly temperatures during continuous leaf wetness
        self._tmeans = []
        # Cumulative continuous leaf wetness duration
        self._leaf_wd = LeafWetnessCounter()
        # Mills table instance
        self._mills_table = _MillsPM()

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with leaf wetness and temperature
        """
        self._leaf_wd.update(update_ctx.lw)
        # Append hourly temperature if the leaf is wet
        if self._leaf_wd.value > 0:
            self._tmeans.append(update_ctx.tmean)
        else:
            self._tmeans.clear()
        # If no leaf wetness then we don't check mills
        if self._leaf_wd.value == 0:
            risk = 0
        else:
            t = sum(self._tmeans) / len(self._tmeans)
            # Use the internal mills table to compute the probability of the
            # ascospore discharge event
            risk = self._mills_table.get_risk(t, self._leaf_wd.value)
        # Add the event for compatibility cast mills risk in float
        self._events.append(DiseaseEvent(
            dt=update_ctx.dt,
            spore_release=float(risk)
        ))


class Caffi(BaseDiseaseWithPhenology):
    """Caffi mechanistic model.

    Use daily temperature, rain, relative humidity and leaf wetness.

    This model tracks a different parameters reported below:

    * PAR: Proportion of ascospores ready for discharge
    * AIC: Ascospores in chasmothecia (ready for discharge)
    * ADR: Ascospores discharge rate
    * AOL: Ascospores reaching the leaf
    * INF: Infection rate
    * COL: Colony-forming ascospores on leaves

    Please note that the AOL and COL are reported respectively as the
    spore_release and infection fields in the DiseaseEvent, while the others
    are included as extra_field.
    """
    _model_meta = {
        "timestep": "d",
        "use_ctx_fields": {
            CtxField.LW,
            CtxField.RAIN,
            CtxField.TMEAN,
            CtxField.RHMEAN,
        },
        "bbch_range": (9, None)
    }

    def __init__(self, phen_model, och=1.0):
        """Initialize the model.

        :param phen_model: a phenological model
        :param och: overwintered chasmothecia (default 1.0)
        """
        super().__init__(phen_model)
        # Check the OCH to be in range ]0, 1]
        if och < 0 or och > 1:
            raise ValueError("OCH must be in range ]0, 1]")
        # Degree-day with 10°C base
        self._dd = 0
        # Overwintered chasmothecia
        self._och = och
        self._inf_mng = InfectionManager(self.__compute_inf_latency)

    @property
    def infections(self) -> List[Dict]:
        """Detected infections with progression."""
        return self._inf_mng.infections

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with daily data.

        :param update_ctx: update context using t, rain, lw
        """
        t = update_ctx.tmean
        r = update_ctx.rain
        lwd = update_ctx.lw
        vpd_d = update_ctx.vpd_h
        # Update growing degree days value
        self._dd += max(t - 10, 0)
        # PAR is the cumulative proportion of mature ascospore
        x = exp(-1.91 * self._dd / 100)
        par = exp(-1.95 * x)
        # When PAR reach 1 then we can stop the model
        if not isclose(par, 1):
            # Initialize output variables to zero
            # aol: Ascospore released reaching the leaf
            # inf: Infection rate
            # col: Ascospore amount creating colony on leaf
            aol = 0
            inf = 0
            col = 0
            # Ascospore maturation daily rate (derivate of PAR)
            amr = par * (-1.95 * x) * (-1.91 / 100)
            # Amount of mature ascospore ready for dispersion
            aic = self._och * amr
            # Ascospore discharge event
            if r > 2 and t > 4 and t < 30:
                # Compute the ascospore daily release rate
                adr = 1 - (0.969 * exp(-0.0004 * lwd * (t ** 2)))
                aol = adr * aic
                # Compute infection risk if conditions are met
                if t >= 5 and t <= 31:
                    # Compute equivalent temperature (0-1)
                    t_eq = equiv_temp(t, (5, 31))
                    # Evaluate infection risk
                    inf = kdbeta(t_eq, 2.403, 0.892, 7.391)
                    inf = inf * exp(-0.221 * vpd_d)
                    # Evaluate colony on leaf
                    col = aol * inf
                    if col > 0:
                        self._inf_mng.add_infection(update_ctx.dt)
            self._events.append(DiseaseEvent(
                dt=update_ctx.dt,
                spore_release=aol,
                infection=col,
                extra_fields={"par": par, "inf": inf}
            ))
            # Finally update the current active infections
            self._inf_mng.update(update_ctx)

    @staticmethod
    def __compute_inf_latency(update_ctx: UpdateCtx) -> float:
        """Infection latency update strategy for Caffi.

        :param update_ctx: the current update context
        :returns: the daily increase for latency computation
        """
        tmean = update_ctx.tmean
        return 1 / (47.256 - (3.604 * tmean) + (0.077 * (tmean ** 2)))
