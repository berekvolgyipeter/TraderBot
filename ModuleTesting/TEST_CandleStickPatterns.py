from BackTesting.TestUtilities import *
import matplotlib.pyplot as plt
from HistoricDataHandler.PriceChartHistory import GetChartData
from ChartingUtilities.CandlestickPatterns import *


def RecogniseCandleStickPatterns(charts: Charts, pattern='Hammer'):
    trigger_queue = TriggerQueue()
    cond = False

    for smpl in range(0, charts.max_len):
        trigger_queue.buy.append([])
        trigger_queue.sell.append([])

        for market_name in charts.close:
            if IsChartIndexInRange(smpl, charts, market_name, offset=5):
                idx = CalculateChartIndex(smpl, charts, market_name)

                if 'Hammer' == pattern:
                    cond = Hammer(charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'BullishEngulfing' == pattern:
                    cond = BullishEngulfing(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                            charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'Piercing' == pattern:
                    cond = Piercing(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                    charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'TweezerBottom' == pattern:
                    cond = TweezerBottom(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                         charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'MorningStar' == pattern:
                    cond = MorningStar(charts.open[market_name][idx-2], charts.high[market_name][idx-2], charts.low[market_name][idx-2], charts.close[market_name][idx-2],
                                       charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                       charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif pattern == 'MorningStar2' == pattern:
                    cond = MorningStar2(charts.open[market_name][idx-3], charts.high[market_name][idx-3], charts.low[market_name][idx-3], charts.close[market_name][idx-3],
                                        charts.open[market_name][idx-2], charts.high[market_name][idx-2], charts.low[market_name][idx-2], charts.close[market_name][idx-2],
                                        charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                        charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'MorningStar3' == pattern:
                    cond = MorningStar3(charts.open[market_name][idx-4], charts.high[market_name][idx-4], charts.low[market_name][idx-4], charts.close[market_name][idx-4],
                                        charts.open[market_name][idx-3], charts.high[market_name][idx-3], charts.low[market_name][idx-3], charts.close[market_name][idx-3],
                                        charts.open[market_name][idx-2], charts.high[market_name][idx-2], charts.low[market_name][idx-2], charts.close[market_name][idx-2],
                                        charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                        charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])



                elif 'ShootingStar' == pattern:
                    cond = ShootingStar(charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'BearishEngulfing' == pattern:
                    cond = BearishEngulfing(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                            charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'DarkCloudCover' == pattern:
                    cond = DarkCloudCover(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                          charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'TweezerTop' == pattern:
                    cond = TweezerTop(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                      charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'EveningStar' == pattern:
                    cond = EveningStar(charts.open[market_name][idx-2], charts.high[market_name][idx-2], charts.low[market_name][idx-2], charts.close[market_name][idx-2],
                                       charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                       charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'EveningStar2' == pattern:
                    cond = EveningStar2(charts.open[market_name][idx-3], charts.high[market_name][idx-3], charts.low[market_name][idx-3], charts.close[market_name][idx-3],
                                        charts.open[market_name][idx-2], charts.high[market_name][idx-2], charts.low[market_name][idx-2], charts.close[market_name][idx-2],
                                        charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                        charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])
                elif 'EveningStar3' == pattern:
                    cond = EveningStar3(charts.open[market_name][idx-4], charts.high[market_name][idx-4], charts.low[market_name][idx-4], charts.close[market_name][idx-4],
                                        charts.open[market_name][idx-3], charts.high[market_name][idx-3], charts.low[market_name][idx-3], charts.close[market_name][idx-3],
                                        charts.open[market_name][idx-2], charts.high[market_name][idx-2], charts.low[market_name][idx-2], charts.close[market_name][idx-2],
                                        charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                        charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])



                elif 'BullishHarami' == pattern:
                    cond = BullishHarami(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                         charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])

                elif 'BearishHarami' == pattern:
                    cond = BearishHarami(charts.open[market_name][idx-1], charts.high[market_name][idx-1], charts.low[market_name][idx-1], charts.close[market_name][idx-1],
                                         charts.open[market_name][idx], charts.high[market_name][idx], charts.low[market_name][idx], charts.close[market_name][idx])



                if cond is True:
                    trigger_queue.buy[idx].append(Trigger(market_name, 0.0))

    return trigger_queue



pcharts = GetChartData(broker='POLONIEX',  # POLONIEX
                       get_data_from='saved_data',  # saved_data, fresh_data_by_api_call
                       year='from_2017',  # 2017, 2018, from_2017
                       resolution='4h',  # 5m, 15m, 30m, 2h, 4h, 1d
                       base_currency='USDT',  # USDT, BTC
                       read_these_charts=['USDT_BTC'])  # None or []: reads all base currency markets

tq = RecogniseCandleStickPatterns(pcharts,
                                  pattern='MorningStar2'
                                  # Hammer, BullishEngulfing, Piercing, TweezerBottom, MorningStar, MorningStar2, MorningStar3
                                  # ShootingStar, BearishEngulfing, DarkCloudCover, TweezerTop, EveningStar, EveningStar2, EveningStar3
                                  # BullishHarami, BearishHarami
                                  )


PlotOHLC(pcharts, trigger_queue=tq)
plt.show()
