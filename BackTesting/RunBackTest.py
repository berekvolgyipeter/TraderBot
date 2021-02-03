from BackTesting.OfflineAlgorithms import *
from BackTesting.Simulation import Simulation
from BackTesting.TestUtilities import *
from HistoricDataHandler.PriceChartHistory import GetChartData
import matplotlib.pyplot as plt


charts = GetChartData(broker='POLONIEX',  # POLONIEX
                      get_data_from='saved_data',  # saved_data, fresh_data_by_api_call
                      year='from_2017',  # 2017, 2018, from_2017
                      resolution='1d',  # 5m, 15m, 30m, 2h, 4h, 1d
                      base_currency='USDT',  # USDT, BTC
                      read_these_charts=['USDT_BTC'])  # []: all markets, ['BTC_ETH', 'BTC_XRP']

"""Getting results of HODL"""
simulation = Simulation(charts)
result_hodl = simulation.Run(Alg_HODL(charts), charts)

"""Getting results of the selected algorithm"""
simulation = Simulation(charts)
trigger_queue = Alg_HODL(charts)
result = simulation.Run(trigger_queue, charts)

PlotResults(result, result_hodl, plot_num_of_trades=False)

PlotOHLC(charts, trigger_queue,
         chart_style='ohlc',  # ohlc, line
         fast_ema=20,
         normal_ema=50,
         slow_ema=200,
         plot_bb=True, bb_sample_num=50, sigma=2,
         rsi=14,
         plot_obv=True,
         plot_volume=True)

""" show plots if there is any"""
plt.show()
