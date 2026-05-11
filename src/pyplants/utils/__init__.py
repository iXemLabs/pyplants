from math import exp


def vpd_h(t, rh):
    """Compute the hourly vapour pressure deficit.

    :param t: hour mean temperature
    :param rh: hour mean relative humidity
    :returns: hourly vpd value
    """
    return (1 - (rh / 100)) * 6.11 * (exp((17.47 * t) / (239 + t)))


def gd_sum(a, base=0):
    """Cumulative temperature sum (only positive) with a given base.

    :param a: the list of values
    :param base: the base temperature
    :returns: the cumulative sum
    """
    r = 0
    for value in a:
        r += max(value - base, 0)
    return r
