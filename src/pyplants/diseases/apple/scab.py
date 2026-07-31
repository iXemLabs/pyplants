from pyplants.core.base import BasePhenology
from pyplants.core.base import BaseDiseaseWithPhenology
from pyplants.core.context import CtxField
from pyplants.core.context import UpdateCtx
from pyplants.utils.mills import MillsTable
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.common import DiseaseEvent


class MillsRI(BaseDiseaseWithPhenology):
    """The classic mills risk model for apple.

    Use hourly mean temperature and leaf wetness to compute:

    * infection risk

    Risk index are mapped on a range [0,1] rather than the usual category.
    """
    _model_meta = {
        "timestep": "h",
        "use_ctx_fields": {CtxField.TMEAN, CtxField.LW},
        "bbch_range": (51, 69)
    }

    def __init__(self, phen_model: BasePhenology):
        """Initialize the model.

        :param phen_model: an apple phenological model
        """
        super().__init__(phen_model)
        # List of hourly temperatures during continuous leaf wetness
        self._tmeans = []
        # Cumulative continuous leaf wetness duration
        self._leaf_wd = LeafWetnessCounter()
        # Mills table instance
        self._mills_table = MillsTable("classic")

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
            # Use the internal mills table to compute infection risk
            risk = self._mills_table.get_risk(t, self._leaf_wd.value)
        # Add the event for compatibility cast mills risk in float
        self._events.append(DiseaseEvent(
            dt=update_ctx.dt,
            infection=float(risk)
        ))
