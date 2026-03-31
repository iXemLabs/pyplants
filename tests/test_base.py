import unittest
from datetime import datetime

from pyplants.core.context import UpdateCtx
from pyplants.utils.helpers import DailyUpdater
from pyplants.utils.helpers import LeafWetnessCounter
from pyplants.diseases.grape.pm import Moyer
from pyplants.phenology.scales import BBCHStage

from utils import load_test_samples


class BaseTest(unittest.TestCase):
    """Base test case for generic models and utility."""

    def test_update_ctx(self):
        """Basic update context checks."""
        # One can no create an update context with no date
        with self.assertRaises(TypeError):
            UpdateCtx(tmean=10, rain=0)
        # Vapoure pressure deficit requires tmean and rhmean fields
        uctx = UpdateCtx(dt=datetime.utcnow(), tmean=0)
        with self.assertRaises(AttributeError):
            uctx.vpd_h

    def test_missing_tmax(self):
        """Missing parameter inside update context."""
        dt = datetime(2026, 1, 1, 0, 0)
        uctx = UpdateCtx(dt=dt, rain=0)
        # The Moyer model requires rain and tmax in context
        moyer = Moyer()
        with self.assertRaises(ValueError):
            moyer.update(uctx)

    def test_bbch(self):
        """BBCH comparison overload."""
        s1 = BBCHStage(vstage=1, rstage=0, dt=datetime(2026, 1, 15, 0, 0))
        s2 = BBCHStage(vstage=5, rstage=0, dt=datetime(2026, 1, 30, 0, 0))
        # Check the overload operator for comparison
        self.assertGreater(s2, s1)
        self.assertGreater(9, s2)

    def test_daily_updater(self):
        """Basic test for the daily updater helper."""
        daily_updater = DailyUpdater([])
        samples = load_test_samples("samples.csv")
        # Update using the first day of the dataset
        for i in range(0, 24):
            daily_updater.update(UpdateCtx(
                dt=samples[i]["DATE"],
                rain=samples[i]["RAIN"],
                tmean=samples[i]["TMEAN"],
                rhmean=samples[i]["RHMEAN"],
                lw=samples[i]["LEAFWETNESS"]))
        self.assertEqual(daily_updater._daily_ctx.tmax, 8.42)
        self.assertEqual(daily_updater._daily_ctx.tmin, 5.87)
        self.assertEqual(daily_updater._daily_ctx.lw, 13)
        self.assertEqual(daily_updater._daily_ctx.rain, 0)
        # Update using data from the next day
        for i in range(24, 48):
            daily_updater.update(UpdateCtx(
                dt=samples[i]["DATE"],
                rain=samples[i]["RAIN"],
                tmean=samples[i]["TMEAN"],
                rhmean=samples[i]["RHMEAN"],
                lw=samples[i]["LEAFWETNESS"]))
        self.assertEqual(daily_updater._daily_ctx.tmax, 8.43)
        self.assertEqual(daily_updater._daily_ctx.tmin, 7.45)
        self.assertEqual(daily_updater._daily_ctx.lw, 24)
        self.assertEqual(daily_updater._daily_ctx.rain, 6)

    def test_leaf_wetness_counter(self):
        """Test the leaf wetness counter."""
        lw = LeafWetnessCounter()
        # Simulate a record: dry, wet, wet
        lw.update(0)
        lw.update(1)
        lw.update(1)
        self.assertEqual(lw.value, 2)
        # Stop the wetness period
        lw.update(0)
        self.assertEqual(lw.value, 0)
        # Restart with one wet record
        lw.update(1)
        self.assertEqual(lw.value, 1)


if __name__ == "__main__":
    unittest.main()
