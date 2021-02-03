import numpy as np
from Configuration.Parameters import *


def FirFilterExp(last_sample, last_ema, N):
    cutoff = 2.0 / (N + 1)
    return (last_sample - last_ema) * cutoff + last_ema


def VolumeWeightedMA(sample_array, volume_array, N):
    return np.average(sample_array[-N:] * volume_array[-N:]) / np.average(volume_array[-N:])


def StandardDev(chart, window=ONE_DAY_WINDOW_5MIN):
    return np.std(chart[-window:], dtype=float, ddof=1)
