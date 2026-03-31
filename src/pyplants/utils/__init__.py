from math import exp


def vpd_h(t, rh):
    """Compute the hourly vapour pressure deficit.

    :param t: hour mean temperature
    :param rh: hour mean relative humidity
    :returns: hourly vpd value
    """
    return (1 - (rh / 100)) * 6.11 * (exp((17.47 * t) / (239 + t)))
