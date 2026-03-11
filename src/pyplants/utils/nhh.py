from math import log
from math import pow
from pyplants.utils.plants import PlantEnum


__nhh_by_crop = {
    PlantEnum.GRAPE.name: (12, 25, 33),
    PlantEnum.OLIVE.name: (7, 26, 35)
}


def get_nhh_params(plant: PlantEnum):
    """Get the tcmin, tcopt and tcmax params for plant.

    :param plant: a PlantEnum value
    :returns: tuple with nhh params (min, opt, max)
    """
    return __nhh_by_crop[plant.name]


class NHH(object):
    """Normal Heat Hours calculator."""

    def __init__(self, tcmin, tcopt, tcmax):
        """Construct the instance for the NHH calculator.

        :param tcmin: minimum temperature for plant activation
        :param tcopt: optimum temperature for plant activity
        :param tcmax: maximum temperature for plant activation
        """
        if tcmin > tcopt or tcopt > tcmax:
            raise ValueError("Invalid cardinal temperature provided")
        self._value = 0
        # Set the internal parameters based on the plant type
        self._tcmin = tcmin
        self._tcmax = tcmax
        self._tcopt = tcopt
        # Compute the alpha internal parameter
        self.__alpha = log(2) / log((tcmax - tcmin) / (tcopt - tcmin))

    @property
    def value(self):
        """Get the current nhh value"""
        return self._value

    def set_params(self, tcmin, tcopt, tcmax):
        """Change cardinal temperatures.

        This operation is allowed only when nhh value is still zero.

        :param tcmin: minimum temperature for plant activation
        :param tcopt: optimum temperature for plant activity
        :param tcmax: maximum temperature for plant activation
        :raises: RuntimeError
        """
        if self._value != 0:
            raise RuntimeError("Can not change params after starting computation")
        if tcmin > tcopt or tcopt > tcmax:
            raise ValueError("Invalid cardinal temperature provided")
        self._tcmin = tcmin
        self._tcopt = tcopt
        self._tcmax = tcmax

    def _to_nhh(self, value):
        """Compute the NHH value from the provided tmean value.

        :param value: the tmean to translate in nhh
        :returns: the NHH value
        """
        if value <= self._tcmin:
            return 0
        if value >= self._tcmax:
            return 0
        p1 = pow(value - self._tcmin, self.__alpha)
        p2 = pow(self._tcopt - self._tcmin, self.__alpha)
        p3 = pow(value - self._tcmin, 2 * self.__alpha)
        p4 = pow(self._tcopt - self._tcmin, 2 * self.__alpha)
        return ((2 * p1 * p2) - p3) / p4

    def update(self, value):
        """Update the NHH value given a scalar value.

        :param value: the scalar value to provide as tmean
        """
        self._value += self._to_nhh(value)

    def get_response_curve(self):
        """Get nhh response curve (useful for debug).

        :returns: a list of tuple (temperature, nhh)
        """
        values = []
        for i in range(self._tcmax + 3):
            values.append((i, self._to_nhh(i)))
        return values

    def __repr__(self):
        """Override default repr to display useful info."""
        return "nhh=%f, [tcmin=%d,tcopt=%d,tcmax=%d]" % (
            self._value, self._tcmin, self._tcopt, self._tcmax)
