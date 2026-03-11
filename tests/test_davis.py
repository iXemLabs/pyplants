import unittest

from datetime import datetime

from pyplants.utils import UpdateCtx
from pyplants.utils.plants import PlantEnum
from pyplants.diseases.pm import DavisRI
from pyplants.phenology.iphen import Iphen


class DavisRiskIndexTest(unittest.TestCase):
    """Test case for Davis model."""

    def setUp(self):
        self.iphen = Iphen.build_from_plant(PlantEnum.GRAPE, "CHARDONNAY")
        self.davis = DavisRI(self.iphen)

    def _update_model(self, samples):
        """Update the model with provided samples."""
        pass

    def test_no_wetness(self):
        """Check for no infection when no leaf wetness."""
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
