import numpy as np
from BackTesting.TestUtilities import CalculateChartIndex, IsChartIndexInRange
from HistoricDataHandler.PriceChartHistory import Charts


def FindMinimaIndexes_rolling(charts: Charts, window=4):
    """
    Returns the indexes of minima
    :return: indexes["market_name"][minima_idx0, ..., minima_idx_n]
    """
    indexes = dict()

    for market_name in charts.close:
        indexes[market_name] = []

        for smpl in range(0, charts.max_len - window):
            if IsChartIndexInRange(smpl, charts, market_name, offset=window):
                idx = CalculateChartIndex(smpl, charts, market_name)
                if((np.min(charts.low[market_name][idx - window:idx]) >= charts.low[market_name][idx]) and
                   (np.min(charts.low[market_name][idx + 1:idx + 1 + window]) >= charts.low[market_name][idx])):
                    indexes[market_name].append(idx)
    return indexes


def FindMaximaIndexes_rolling(charts: Charts, window=4):
    """
    Returns the indexes of maxima
    :return: indexes["market_name"][maxima_idx0, ..., maxima_idx_n]
    """
    indexes = dict()

    for market_name in charts.close:
        indexes[market_name] = []

        for smpl in range(0, charts.max_len - window):
            if IsChartIndexInRange(smpl, charts, market_name, offset=window):
                idx = CalculateChartIndex(smpl, charts, market_name)
                if((np.max(charts.high[market_name][idx - window:idx]) <= charts.high[market_name][idx]) and
                   (np.max(charts.high[market_name][idx + 1:idx + 1 + window]) <= charts.high[market_name][idx])):
                    indexes[market_name].append(idx)
    return indexes


def InterpolateExtremas(charts: Charts, idx_of_extremas, find='highs'):
    """
    Returns an interpolation between given extremas
    """
    interpolation = dict()
    extrema_values = dict()

    for market_name in charts.close:
        extrema_values[market_name] = []
        if 0 != idx_of_extremas[market_name][0]:
            idx_of_extremas[market_name].insert(0, 0)
        if idx_of_extremas[market_name][-1] is not (charts.chart_lengths[market_name] - 1):
            idx_of_extremas[market_name].append(charts.chart_lengths[market_name] - 1)

        if 'highs' == find:
            for idx in range(0, len(idx_of_extremas[market_name])):
                extrema_values[market_name].append(charts.high[market_name][idx_of_extremas[market_name][idx]])
        else:  # 'lows'
            for idx in range(0, len(idx_of_extremas[market_name])):
                extrema_values[market_name].append(charts.low[market_name][idx_of_extremas[market_name][idx]])

        interpolation[market_name] = np.interp(np.arange(0, charts.chart_lengths[market_name]),
                                               idx_of_extremas[market_name],
                                               extrema_values[market_name])

    return interpolation


def FindLowsBelowInterpolation(charts: Charts, interp_line, idx_of_minima):
    """
    Returns the indexes of those candles whose distance is the greatest from a given interpolation line.
    Only returns those indexes which's candle is beyond the interpolation line.
    (when candle low is less than the interpolation of minima)
    """
    ret = dict()

    for market_name in charts.close:
        ret[market_name] = []
        less = np.less(charts.low[market_name], interp_line[market_name])
        idx_of_minima_looper = 0
        for smpl in range(0, charts.max_len):
            if IsChartIndexInRange(smpl, charts, market_name, offset=0):
                idx = CalculateChartIndex(smpl, charts, market_name)

                if idx == idx_of_minima[market_name][idx_of_minima_looper + 1]:
                    if True in less[idx_of_minima[market_name][idx_of_minima_looper] + 1:
                                    idx_of_minima[market_name][idx_of_minima_looper + 1]]:
                        if idx == idx_of_minima[market_name][idx_of_minima_looper + 1]:
                            diff = interp_line[market_name][idx_of_minima[market_name][idx_of_minima_looper] + 1:
                                                            idx_of_minima[market_name][idx_of_minima_looper + 1]] \
                                   - charts.low[market_name][idx_of_minima[market_name][idx_of_minima_looper] + 1:
                                                             idx_of_minima[market_name][idx_of_minima_looper + 1]]
                            ret[market_name].append(idx_of_minima[market_name][idx_of_minima_looper] + 1 + np.argmax(diff))
                    idx_of_minima_looper += 1
    return ret


def FindHighsBeyondInterpolation(charts: Charts, interp_line, idx_of_maxima):
    """
    Returns the indexes of those candles whose distance is the greatest from a given interpolation line.
    Only returns those indexes which's candle is beyond the interpolation line.
    (when Candle high is greater than the interpolation of maxima)
    """
    ret = dict()

    for market_name in charts.close:
        ret[market_name] = []
        greater = np.greater(charts.high[market_name], interp_line[market_name])
        idx_of_maxima_looper = 0
        for smpl in range(0, charts.max_len):
            if IsChartIndexInRange(smpl, charts, market_name, offset=0):
                idx = CalculateChartIndex(smpl, charts, market_name)

                if idx == idx_of_maxima[market_name][idx_of_maxima_looper + 1]:
                    if True in greater[idx_of_maxima[market_name][idx_of_maxima_looper] + 1:
                                       idx_of_maxima[market_name][idx_of_maxima_looper + 1]]:
                        if idx == idx_of_maxima[market_name][idx_of_maxima_looper + 1]:
                            diff = charts.high[market_name][idx_of_maxima[market_name][idx_of_maxima_looper] + 1:
                                                            idx_of_maxima[market_name][idx_of_maxima_looper + 1]] \
                                   - interp_line[market_name][idx_of_maxima[market_name][idx_of_maxima_looper] + 1:
                                                              idx_of_maxima[market_name][idx_of_maxima_looper + 1]]
                            ret[market_name].append(idx_of_maxima[market_name][idx_of_maxima_looper] + 1 + np.argmax(diff))
                    idx_of_maxima_looper += 1
    return ret


def FindLowerTrendLine(charts: Charts, window=50, num_of_peaks=3, max_dist=0.04):
    ret = dict()
    step = int(0.00 * window)
    if 0 == step:
        step = 1

    for market_name in charts.close:
        ret[market_name] = []
        start_idx = []
        slope = []
        offset = []
        x = range(0, charts.chart_lengths[market_name])
        y = charts.low[market_name]
        DEBUG_num_of_lines = 0

        if (window + 1) < charts.chart_lengths[market_name]:  # +1 offset is needed because of condition '# the first touch is a 2 minima from the left'
            for idx in np.arange(window + 1, charts.chart_lengths[market_name], step):
                idx0 = idx - window + 1
                idx1 = idx + 1
                if y[idx0] == min(y[idx0-2:idx0+1]):  # the first candle must be a 2 minima from the left
                    less_than_max_dist = False
                    price_range = max(charts.high[market_name][idx0:idx1]) - min(charts.low[market_name][idx0:idx1])
                    x_del = x[idx0:idx1]
                    y_del = y[idx0:idx1]

                    """Performing linear regression (indexing is relative to idx)"""
                    while (len(x_del) > num_of_peaks) and not less_than_max_dist:
                        linreg = np.polyfit(x_del, y_del, 1)
                        to_remove = np.where(y_del > (linreg[0] * x_del + linreg[1]))[0]  # indices where low is above regression line
                        if 0 in to_remove:  # The first candle is never removed
                            to_remove = np.delete(to_remove, 0)
                        x_del = np.delete(x_del, to_remove)
                        y_del = np.delete(y_del, to_remove)
                        dist = ((linreg[0] * x[idx0:idx1] + linreg[1]) - y[idx0:idx1]) / price_range  # relative distance from linear regression line
                        if max(dist) <= max_dist:
                            less_than_max_dist = True  # break
                            idx_of_touches = np.where((-max_dist / 2.0) <= dist)[0]  # relative to idx
                            dist_between_touches = idx_of_touches[1:] - idx_of_touches[:-1]

                    """Filtering false trend lines"""
                    # <warning suppress> In the above while loop dist, linreg, idx_of_touches and dist_between_touches get value.
                    # <warning suppress> If we do not enter into the loop then less_than_max_dist stays False and thus the variables are not used.
                    if(less_than_max_dist and
                       (idx_of_touches[-1] >= int(0.6 * window)) and  # the last touch is in the last 40% of the trendline
                       (max(dist_between_touches) < int(0.5 * window))  # maximum distance between any two touches is 50% of trendline length
                       ):

                        if(  # check whether a previous trendline can be updated or this one will be added
                           start_idx and
                           (idx0 - start_idx[-1] < window) and  # If the new line is within 'window' distance from the previous
                           ((abs(slope[-1] - linreg[0]) / abs(linreg[0])) < 0.1) and  # If the new line is very similar to the previous
                           ((abs(offset[-1] - linreg[1]) / abs(linreg[1])) < 0.1)
                           ):
                            """Performing linear regression again with the wider range (indexing is relative to idx)"""
                            # less_than_max_dist = False
                            # idx0 = start_idx[-1]
                            # idx1 = idx + 1
                            # x_del = x[idx0:idx1]
                            # y_del = y[idx0:idx1]
                            # while (len(x_del) > num_of_peaks) and not less_than_max_dist:
                            #     linreg = np.polyfit(x_del, y_del, 1)
                            #     to_remove = np.where(y_del > (linreg[0] * x_del + linreg[1]))[0]
                            #     x_del = np.delete(x_del, to_remove)
                            #     y_del = np.delete(y_del, to_remove)
                            #     dist = ((linreg[0] * x[idx0:idx1] + linreg[1]) - y[idx0:idx1]) / y[idx0:idx1]  # relative distance from linear regression line
                            #     if max(dist) <= max_dist:
                            #         less_than_max_dist = True
                            # """Replacing last elements in ret"""
                            # ret[market_name][-1] = np.asarray(linreg[0] * x + linreg[1])
                            # ret[market_name][-1][0:idx0] = float('nan')
                            # ret[market_name][-1][idx1:] = float('nan')
                            # start_idx[-1] = idx0
                            # slope[-1] = linreg[0]
                            # offset[-1] = linreg[1]

                        else:
                            ret[market_name].append(np.asarray(linreg[0] * x + linreg[1]))
                            ret[market_name][-1][0:idx0] = float('nan')
                            ret[market_name][-1][idx1:] = float('nan')
                            start_idx.append(idx0)
                            slope.append(linreg[0])
                            offset.append(linreg[1])
                            DEBUG_num_of_lines += 1
        print(DEBUG_num_of_lines)
    return ret
