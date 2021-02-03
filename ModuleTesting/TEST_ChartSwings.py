from BackTesting.TestUtilities import *
import matplotlib.pyplot as plt
from HistoricDataHandler.PriceChartHistory import GetChartData
from ChartingUtilities.ChartSwings import *


def FindMaximaWithEMA(charts: Charts, window=9):
    trigger_queue = TriggerQueue()
    ema = dict()
    grad = dict()

    for market_name in charts.close:
        ema[market_name] = EMA_rolling(charts.high[market_name], window=window)
        grad[market_name] = np.gradient(ema[market_name])

    for smpl in range(0, charts.max_len):
        trigger_queue.buy.append([])
        trigger_queue.sell.append([])

    for smpl in range(0, charts.max_len-9):
        for market_name in charts.close:
            if IsChartIndexInRange(smpl, charts, market_name, offset=window):
                idx = CalculateChartIndex(smpl, charts, market_name)

                if (grad[market_name][idx] < 0.0) and (grad[market_name][idx-1] > 0.0):
                    add_idx = np.argmax(charts.high[market_name][idx-9:idx+1]) - 9

                    trigger_queue.sell[smpl+add_idx].append(Trigger(market_name, 0.0))

    return trigger_queue


def FindExtremas(charts: Charts, indexes_min, indexes_max, window=4):
    trigger_queue = TriggerQueue()

    for smpl in range(0, charts.max_len):
        trigger_queue.buy.append([])
        trigger_queue.sell.append([])

    for market_name in charts.close:
        for smpl in range(0, charts.max_len-window):
            if IsChartIndexInRange(smpl, charts, market_name, offset=window):
                idx = CalculateChartIndex(smpl, charts, market_name)
                if idx in indexes_min[market_name]:
                    trigger_queue.buy[smpl].append(Trigger(market_name, 0.0))
                if idx in indexes_max[market_name]:
                    trigger_queue.sell[smpl].append(Trigger(market_name, 0.0))

    return trigger_queue


def FindInterpSwingLows(charts: Charts, interp_lows, idx_lows, interp_highs, idx_highs):
    trigger_queue = TriggerQueue()
    extra_lows = FindLowsBelowInterpolation(charts, interp_lows, idx_lows)
    extra_highs = FindHighsBeyondInterpolation(charts, interp_highs, idx_highs)
    for smpl in range(0, charts.max_len):
        trigger_queue.buy.append([])
        trigger_queue.sell.append([])

    for market_name in charts.close:
        for smpl in range(0, charts.max_len):
            if IsChartIndexInRange(smpl, charts, market_name, offset=0):
                idx = CalculateChartIndex(smpl, charts, market_name)
                if idx in extra_lows[market_name]:
                    trigger_queue.buy[smpl].append(Trigger(market_name, 0.0))
                if idx in extra_highs[market_name]:
                    trigger_queue.sell[smpl].append(Trigger(market_name, 0.0))
    return trigger_queue


pcharts = GetChartData(broker='POLONIEX',  # POLONIEX
                       get_data_from='saved_data',  # saved_data, fresh_data_by_api_call
                       year='from_2017',  # 2017, 2018, from_2017
                       resolution='1d',  # 5m, 15m, 30m, 2h, 4h, 1d
                       base_currency='USDT',  # USDT, BTC
                       read_these_charts=['USDT_BTC'])  # None or []: reads all base currency markets


# idxs_min = FindMinimaIndexes_rolling(pcharts, window=4)
# idxs_max = FindMaximaIndexes_rolling(pcharts, window=4)
# interp_low = InterpolateExtremas(pcharts, idxs_min, find='lows')
# interp_high = InterpolateExtremas(pcharts, idxs_max, find='highs')
# tq = FindMaximaWithEMA(pcharts, window=9)
# tq = FindExtremas(pcharts, idxs_min, idxs_max)
# tq = FindInterpSwingLows(pcharts, interp_low, idxs_min, interp_high, idxs_max)
trend = FindLowerTrendLine(pcharts, num_of_peaks=3, window=20)

PlotOHLC(pcharts,
         # trigger_queue=tq,
         extra_plot1=trend,
         # extra_plot2=interp_high
         )
plt.show()
