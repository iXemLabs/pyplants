from math import exp
from math import nan
from collections import deque

from pyplants.core.base import BaseDiseaseWithPhenology
from pyplants.core.context import UpdateCtx
from pyplants.core.context import CtxField
from pyplants.utils import kdbeta
from pyplants.utils import equiv_temp
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.common import DiseaseEvent
from pyplants.diseases.common import GenericMagarey


class Broome(BaseDiseaseWithPhenology):
    """Broome GM model.

    Use hourly temperature and leaf wetness to compute:

    * infection risk

    This module compute infection risk during continuous leaf wetness periods
    counted using a dry_off equals to 4h.
    """
    _model_meta = {
        "timestep": "h",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.LW},
        "bbch_range": (65, 89)
    }

    def __init__(self, phen_model):
        """Init the model.

        :param phen_model: a grape phenological model
        """
        super().__init__(phen_model)
        # A leaf wetness counter
        self._leaf_wd = LeafWetnessCounter(dry_off=4)
        # List of temperature during wet period
        self._tmeans = []

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with temperature and leaf wetness
        """
        inf = 0
        self._leaf_wd.update(update_ctx.lw)
        # Check to be in a leaf wetness period
        if self._leaf_wd.value > 0:
            # Accumulate the temperatures during wet period
            self._tmeans.append(update_ctx.tmean)
            # Compute the mean during wet period
            t = sum(self._tmeans) / len(self._tmeans)
            # Compute the Broome index using temperature and wetness hours
            w = self._leaf_wd.value
            index = -2.647866 - (0.374927 * w) + (0.061601 * w * t) \
                - (0.001511 * w * (t ** 2))
            index = exp(index)
            inf = index / (1 + index)
        else:
            self._tmeans.clear()
        self._events.append(DiseaseEvent(dt=update_ctx.dt, infection=inf))


class GoFe(BaseDiseaseWithPhenology):
    """González-Fernández risk periods model (GM).

    Use hourly temperature and leaf wetness to compute:

    * infection risk

    This model is based on the Magarey model and operate differently during
    flowering and ripening.
    """
    _model_meta = {
        "timestep": "h",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.LW}
    }

    def __init__(self, phen_model):
        """Init the model.

        :param phen_model: a grape phenological model
        """
        super().__init__(phen_model)
        # Flowering parameters
        self._magarey_flowering = GenericMagarey((1, 25, 34), 1, 12, 13)
        # Ripening parameters
        self._magarey_ripening = GenericMagarey((10, 20, 35), 4, 10, 13)

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with hourly data.

        :param update_ctx: update context with temperature and leaf wetness
        """
        infection = 0
        magarey_model = None
        if self._phen_model.scale.in_range(65, 68):
            magarey_model = self._magarey_flowering
        elif self._phen_model.scale.in_range(81, 89):
            magarey_model = self._magarey_ripening
        # Check if one of the two models has been selected
        if magarey_model is not None:
            magarey_model.update(update_ctx)
            infection = int(magarey_model.has_infection)
        self._events.append(DiseaseEvent(dt=update_ctx.dt, infection=infection))


class GoDom(BaseDiseaseWithPhenology):
    """González-Domínguez mechanistic (GM).

    Use daily temperature, rh and leaf wetness to compute:

    * infection risk

    This model accounts for conidia production on various inoculum sources and
    for multiple infection pathways.
    """
    _model_meta = {
        "timestep": "d",
        "use_ctx_fields": {CtxField.RHMEAN, CtxField.TMEAN, CtxField.LW}
    }

    def __init__(self, phen_model):
        """Initialize the model."""
        super().__init__(phen_model)
        # Temperatures for mycelial growth (°C)
        self._T_MYGR = (0, 40)
        # Temperature for sporulation (°C)
        self._T_SPOR = (0, 35)
        # Sliding window of 7 days to store parameters for conidia computation
        self._ciso = deque(maxlen=7)

    def _update_imp(self, update_ctx: UpdateCtx):
        """Update the model with daily data.

        Please note that some original formulas have been rewritten using the
        Horner's method.

        :param update_ctx: the update context with temperature and leaf wetness
        """
        rh = update_ctx.rhmean
        lwd = update_ctx.lw
        tmean = update_ctx.tmean
        # Output variables
        infection = 0
        extra_fields = {
            "mygr": nan,
            "ciso": nan,
            "sus1": nan,
            "sus2": nan,
            "sus3": nan,
            "inf_rate1": nan,
            "inf_rate2": nan,
            "inf_rate3": nan,
            "inf2": nan,
            "inf3": nan
        }
        # Factor accounting for moisture
        mf = update_ctx.lw / 24
        # Compute the mycelium growth rate
        teq = equiv_temp(tmean, self._T_MYGR)
        mygr = mf * kdbeta(teq, 0.9, 0.475, 3.78)
        # Compute the spore production rate
        teq = equiv_temp(tmean, self._T_SPOR)
        spor_1 = kdbeta(teq, 0.9, 10.49, 3.7)
        spor_2 = -3.595 + (rh * (0.097 - (0.0005 * rh)))
        spor = spor_1 * spor_2
        # Store the product of spor and mygr in the queue
        self._ciso.append(mygr * spor)
        ciso = sum(self._ciso) / len(self._ciso)
        # Update the extra fields
        extra_fields.update(mygr=mygr, ciso=ciso)
        # The model behaves differently based on infection windows
        if self._phen_model.scale.in_range(53, 73):
            # Compute infection of the first window
            infection, sus1, inf_rate1 = self.__get_inf_risk1(teq, lwd, ciso)
            extra_fields.update(sus1=sus1, inf_rate1=inf_rate1)
        elif self._phen_model.scale.in_range(79, 89):
            # Compute infection severity 2
            inf2, sus2, inf_rate2 = self.__get_inf_risk2(teq, lwd, ciso)
            extra_fields.update(sus2=sus2, inf_rate2=inf_rate2)
            # Compute infection serverity 3
            teq = equiv_temp(tmean, (0, 30))
            inf3, sus3, inf_rate3 = self.__get_inf_risk3(teq, lwd, rh, mygr)
            extra_fields.update(sus3=sus3, inf_rate3=inf_rate3)
            # Store the infection as the sum
            infection = inf2 + inf3
            # Add the single infection risk as additional parameters
            extra_fields["inf2"] = inf2
            extra_fields["inf3"] = inf3
        self._events.append(DiseaseEvent(
            dt=update_ctx.dt, infection=infection, extra_fields=extra_fields))

    def __get_inf_risk1(self, teq: float, lwd: int, ciso: float) -> float:
        """Compute infection severity on inflorescences and young clusters.

        :param teq: the equivalent temperature on 0° and 35°C
        :param lwd: the leaf wetness duration in hours
        :param ciso: the current conidia abundance
        :returns:
            - risk - infection risk (0...1)
            - sus - the relative susceptibility (SUS1)
            - inf_rate - the infection rate (INF1)
        """
        gs = self._phen_model.scale.get_last_stage("r").code / 100
        # Compute relative susceptibility
        sus = 75.209 + (gs * (-390.33 + gs * (671.25 - (379.09 * gs))))
        # Compute the infection rate
        inf_rate = kdbeta(teq, 0.99, 0.71, 3.56)
        inf_rate /= (1 + exp(1.85 - (0.19 * lwd)))
        inf_rate *= sus
        # Compute the relative infection severity
        risk = inf_rate * ciso
        return risk, sus, inf_rate

    def __get_inf_risk2(self, teq: float, lwd: int, ciso: float) -> float:
        """Compute infection severity on ripening berries (conidial infection).

        :param teq: the equivalent temperature on 0°C and 35°C
        :param lwd: the leaf wetness duration in hours
        :param ciso: the current conidia abundance
        :returns:
            - risk - infection risk (0...1)
            - sus - the relative susceptibility (SUS2)
            - inf_rate - the infection rate (INF2)
        """
        gs = self._phen_model.scale.get_last_stage("r").code
        # Compute relative susceptibility
        sus = 5 * (10 ** -17) * exp(0.4219 * gs)
        # Compute the infection rate
        inf_rate = kdbeta(teq, 1.292, 0.469, 6.416)
        inf_rate *= exp(-2.3 * exp(-0.048 * lwd))
        inf_rate *= sus
        # Compute the relative infection severity
        risk = inf_rate * ciso
        return risk, sus, inf_rate

    def __get_inf_risk3(self, teq: float, lwd: int, rh: float, mygr: float) -> float:
        """Compute infection severity for berry-to-berry.

        :param teq: the equivalent temperature on 0°C and 30°C
        :param lwd: the leaf wetness duration in hours
        :param rh: the relative humidity in percentage
        :param mygr: the mycelium growth rate
        :returns:
            - risk - infection risk (0...1)
            - sus - the relative susceptibility (SUS3)
            - inf_rate - the infection rate (INF3)
        """
        gs = self._phen_model.scale.get_last_stage("r").code
        # Compute the relative susceptibility
        sus = (0.0546 * gs) - 3.87
        sus = min(sus, 1)
        # Compute the infection rate
        rh /= 100
        inf_rate = kdbeta(teq, 2.14, 0.469, 7.75)
        inf_rate /= (1 + exp(35.36 - (40.26 * rh)))
        inf_rate *= sus
        # Compute the relative infection severity
        risk = inf_rate * mygr
        return risk, sus, inf_rate
