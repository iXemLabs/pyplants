import csv

from enum import IntEnum
from typing import List
from typing import Dict
from importlib.resources import read_text


class MillsRisk(IntEnum):
    """Mills table risk index.

    Models using a mills table should not use directly this enum since
    we prefer to normalize the risk in a range [0,1].
    """
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class MillsTable:
    """The mills table.

    Users may defined a custom table by providing one in the table argument.
    If :code:`save_in_registry` is set to True, the name must be unique, since
    the provided table will be registered.

    A custom table can be defined in the following way:

    :code:`[{"t": 10, "thresholds": [(15, MillsRisk.LOW),...]}, ...]`

    In case no table is provided, we try to load one from the built-in list,
    currently we support the following tables:

    * classic (apple scab)
    * davis (grape powdery mildew)
    """

    def __init__(self, name: str, table: List[Dict] = None, save_in_registry=False):
        """Initialize a mills table.

        :param name: the name of the mills table
        :param table: the table as list of dict
        :param save_in_registry: wether to save the table or not
        :raises ValueError: unknown or malformed table
        """
        if table is not None:
            self.__validate_table(table)
            _table = table
            if save_in_registry:
                _MillsRegistry.add_table(name, table)
        else:
            _table = _MillsRegistry.get(name)
            if _table is None:
                _MillsRegistry.load_table(name)
                _table = _MillsRegistry.get(name)
        self.__table = _table

    def get_risk(self, t: float, lwd: int) -> float:
        """Get the risk reported in the table.

        :param t: the mean temperature in the wetness period
        :param lwd: number of hours of leaf wetness
        :returns: the risk reported in the table normalized
        """
        risk = MillsRisk.NONE
        tmin = self.__table[0]["t"]
        tmax = self.__table[-1]["t"]
        if t >= tmin and t <= tmax:
            # Get the nearest absolute temperature
            row = min(self.__table, key=lambda x: abs(x["t"] - t))
            # Get the risk checking the leaf wetness
            for threshold in row["thresholds"]:
                if lwd < threshold[0]:
                    break
                else:
                    risk = threshold[1]
        return round(risk.value / 3, 2)

    @staticmethod
    def __validate_table(table: List[Dict]):
        for entry in table:
            if "t" not in entry or "thresholds" not in entry:
                raise ValueError("Malformed entry in table")


class _MillsRegistry:
    _registry = {}
    _builtin_tables = {"classic", "davis"}

    @classmethod
    def load_table(cls, name: str):
        """Load built-in table from disk.

        :param name: the name of the mills table
        :raises ValueError: on an unknown table name
        """
        if name not in cls._builtin_tables:
            raise ValueError("Unknown mills table")
        # If table already loaded do nothing
        if name in cls._registry:
            return
        # Load the table and add to registry
        cls._registry[name] = cls.__load_table(name)

    @classmethod
    def add_table(cls, name: str, table: List[Dict]):
        """Add a custom provided table to registry.

        :param name: the name of the table
        :param table: the table as list of dict
        :raises ValueError: caused by malformed table or name already defined
        """
        if name in cls._registry:
            raise ValueError("Double definition of mills table")
        cls._registry[name] = table

    @classmethod
    def get(cls, name: str) -> List[Dict]:
        """Get a table in registry."""
        if name not in cls._registry:
            return None
        return cls._registry[name]

    @staticmethod
    def __load_table(name: str) -> List[Dict]:
        """Load a Mills table from pyplants data.

        Each entry of the resulting table is composed by a dict as follows:

        * t: mean temperature
        * thresholds: list of tuple (wetness, risk)

        :param name: the name of the internal table to load
        :returns: the mills table as a list of dict with temperature and wetness
        """
        table = []
        name = "mills_%s.csv" % name
        data = read_text("pyplants.data", name).splitlines()
        reader = csv.DictReader(data, quoting=csv.QUOTE_NONNUMERIC)
        # Each row has a specific mean temperature value
        for row in reader:
            entry = {"t": row["t"], "thresholds": []}
            # Create the list of risks (skip the fist: NONE)
            for risk_category in list(MillsRisk)[1:]:
                rc = risk_category.name
                if row[rc]:
                    entry["thresholds"].append((row[rc], risk_category))
            table.append(entry)
        return table
