from math import exp
from typing import Tuple
from typing import List


def vpd_h(t: float, rh: float) -> float:
    """Compute the hourly vapor pressure deficit.

    :param t: hourly mean temperature
    :param rh: hourly mean relative humidity
    :returns: hourly vapor pressure deficit
    """
    return (1 - (rh / 100)) * 6.11 * (exp((17.47 * t) / (239 + t)))


def gd_sum(a: List[float], base: float = 0) -> float:
    """Cumulative temperature (only positive) with a given base.

    :param a: the list of values
    :param base: the base temperature
    :returns: the cumulative sum
    """
    r = 0
    for value in a:
        r += max(value - base, 0)
    return r


def equiv_temp(t: float, trange: Tuple[int, int]) -> float:
    """Compute the equivalent temperature in the give range.

    Teq = (t - Tmin) / (Tmax - Tmin), for t in trange
    Teq = 0, otherwise

    :param t: the given temperature
    :param trange: a tuple with (Tmin, Tmax)
    :returns: the equivalent temperature
    """
    if t < trange[0] or t > trange[1]:
        return 0
    return (t - trange[0]) / (trange[1] - trange[0])


def kdbeta(x: float, a: float, b: float, C: float = 1) -> float:
    """Scaled version of beta distribution kernel.

    The function is defined as:

    y = (C * t^a * (1-t))^b

    :param x: the independent variable
    :param a: first exponent
    :param b: second exponent
    :param C: optional scaling factor
    :returns: the value of the beta distribution kernel
    """
    if x < 0 or x > 1:
        raise ArithmeticError("Function defined in [0, 1]")
    return (C * (x ** a) * (1 - x)) ** b
