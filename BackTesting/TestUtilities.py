import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick2_ohlc, volume_overlay
from ChartingUtilities.RollingIndicators import *
import numpy as np


"""---------- global variables ----------"""
TEST_GLOBAL_plt_fig_num = 0

"""---------- ---------------- ----------"""


"""---------- classes ----------"""
class Position:
    def __init__(self, market_name):
        self.market_name = market_name
        self.entering_price = 0.0
        self.entering_price_adjusted = 0.0
        self.num_of_entries = 0
        self.max_price = 0.0
        self.in_position = False


class Trigger:
    def __init__(self, market_name, amount):
        """market name which is referred by the trigger"""
        self.market_name = market_name
        """amount to buy or sell from the selected market"""
        self.amount = amount


class TriggerQueue:
    def __init__(self):
        self.buy = []
        self.sell = []
        self.traded_coins = []


"""---------- utility functions ----------"""
def IsChartIndexInRange(global_index, charts: Charts, market_name, offset=0):
    if global_index >= (charts.max_len - charts.chart_lengths[market_name]) + offset:
        ret = True
    else:
        ret = False
    return ret


def CalculateChartIndex(global_index, charts: Charts, market_name):
    # global_index - (charts.max_len - charts.chart_lengths[market_name])
    return global_index - charts.max_len + charts.chart_lengths[market_name]


def GetTopVolumeCoins(charts: Charts, number_of_coins=30, time_step=96):
    ret = []
    for smpl in range(0, charts.max_len):
        if smpl % time_step == 0:
            top_str = []
            top_volume = []
            for market_name in charts.base_volume:
                if IsChartIndexInRange(smpl, charts, market_name, offset=0):
                    index = CalculateChartIndex(smpl, charts, market_name)

                    if len(top_volume) < number_of_coins:
                        top_volume.append(charts.base_volume[market_name][index])
                        top_str.append(market_name)
                    else:
                        min_top_volume = min(top_volume)
                        if charts.base_volume[market_name][index] > min_top_volume:
                            index_min_top_volume = top_volume.index(min_top_volume)
                            del (top_str[index_min_top_volume])
                            del (top_volume[index_min_top_volume])
                            top_volume.append(charts.base_volume[market_name][index])
                            top_str.append(market_name)
            ret.append(top_str)
        else:
            ret.append(ret[-1])
    return ret


def GetTopVolumeCoins_Old(charts: Charts, number_of_coins=30, time_step=96):
    """This coin slection method was used in the online test started at 2018.05.15."""
    ret = []
    for smpl in range(0, charts.max_len):
        if smpl % time_step == 1:
            top_str = []
            top_volume = []
            for market_name in charts.base_volume:
                if IsChartIndexInRange(smpl, charts, market_name, offset=0):
                    index = CalculateChartIndex(smpl, charts, market_name)

                    if len(top_volume) < number_of_coins:
                        top_volume.append(charts.base_volume[market_name][index])
                        top_str.append(market_name)
                    elif charts.base_volume[market_name][index] > min(top_volume):
                        del (top_volume[top_volume.index(min(top_volume))])
                        del (top_str[top_volume.index(min(top_volume))])
                        top_volume.append(charts.base_volume[market_name][index])
                        top_str.append(market_name)
            ret.append(top_str)
        else:
            try:
                ret.append(ret[-1])
            except IndexError:
                ret.append([])
    return ret


def GetCoinsWithGivenMinVolume(charts: Charts, min_base_volume=30, time_step=96):
    ret = []
    base_volume_ema = dict()
    for market_name in charts.close:
        base_volume_ema[market_name] = EMA_rolling(charts.base_volume[market_name], window=time_step)

    for smpl in range(0, charts.max_len):
        if smpl % time_step == 0:
            selected_markets = []
            for market_name in charts.close:
                if IsChartIndexInRange(smpl, charts, market_name, offset=time_step):
                    index = CalculateChartIndex(smpl, charts, market_name)

                    if base_volume_ema[market_name][index] > min_base_volume:
                        selected_markets.append(market_name)
            ret.append(selected_markets)
        else:
            ret.append(ret[-1])
    return ret


"""---------- data collector functions ----------"""




"""---------- converter functions ----------"""
def ConvertTriggersForResultPlot(_result_hodl, _trigger_queue):
    ret = dict()
    length = len(_result_hodl)
    ret["buy"] = np.full(length, float('nan'))
    ret["sell"] = np.full(length, float('nan'))

    for smpl in range(0, length):
        if _trigger_queue[smpl]["buy"]:
            ret["buy"][smpl] = _result_hodl[smpl]
        if _trigger_queue[smpl]["sell"]:
            ret["sell"][smpl] = _result_hodl[smpl]
    return ret


def ConvertTriggersForPlot(_charts: Charts, _trigger_queue: TriggerQueue):
    ret = {"buy": dict(), "sell": dict()}
    max_values = dict()

    for market_name in _charts.close:
        ret["buy"][market_name] = np.full(_charts.chart_lengths[market_name], float('nan'))
        ret["sell"][market_name] = np.full(_charts.chart_lengths[market_name], float('nan'))
        max_values[market_name] = max(_charts.close[market_name])

    for smpl in range(0, _charts.max_len):
        for trigger in _trigger_queue.buy[smpl]:
            market_name = trigger.market_name
            index = smpl - _charts.max_len + _charts.chart_lengths[market_name]
            ret["buy"][market_name][index] = _charts.low[market_name][index]
        for trigger in _trigger_queue.sell[smpl]:
            market_name = trigger.market_name
            index = smpl - _charts.max_len + _charts.chart_lengths[market_name]
            ret["sell"][market_name][index] = _charts.high[market_name][index]

    return ret


"""---------- plotting functions ----------"""
def PlotTwoCharts(chart1, chart2):
    global TEST_GLOBAL_plt_fig_num
    TEST_GLOBAL_plt_fig_num += 1
    plt.figure(TEST_GLOBAL_plt_fig_num)
    plt.plot(chart1, label='poloniex chart data')
    plt.plot(chart2, label='bittrex chart data')
    plt.legend()
    plt.grid(True)
    plt.title("Chart data")


def DrawVerticalLine(event):
    if not event.inaxes:
        print("not in axes")
    else:
        line = plt.axvline(x=event.xdata, color='black', linestyle='-', alpha=.5)
        line.set_xdata(event.xdata)


def PlotResults(_result, _result_hodl, plot_num_of_trades=True):
    print("Plotting results...")

    """arrange subplots"""
    if plot_num_of_trades:
        big_rowspan = 70
        small_rowspan = 15
        buy_pos = big_rowspan
        sell_pos = buy_pos + small_rowspan
    else:
        big_rowspan = 100
        small_rowspan = 0
        buy_pos = 0
        sell_pos = 0

    global TEST_GLOBAL_plt_fig_num
    TEST_GLOBAL_plt_fig_num += 1
    plt.figure(TEST_GLOBAL_plt_fig_num)

    ax1 = plt.subplot2grid((100, 1), (0, 0), rowspan=big_rowspan, colspan=1)

    ax1.plot(_result["net_profit"], color='C0', label='Algorithm')
    ax1.plot(_result_hodl["net_profit"], color='C1', label='HODL')
    ax1.set_ylabel("Net profit in %")
    ax1.legend()
    ax1.grid(True)
    ax1.set_title("Result")

    if plot_num_of_trades:
        x = np.arange(len(_result["net_profit"]))
        ax2 = plt.subplot2grid((100, 1), (buy_pos, 0), sharex=ax1, rowspan=small_rowspan, colspan=1)
        ax2.plot(x, _result["coins_bought"], color='g', label='Number of buy triggers')
        ax2.legend()
        ax2.grid()

        ax3 = plt.subplot2grid((100, 1), (sell_pos, 0), sharex=ax1, rowspan=small_rowspan, colspan=1)
        ax3.plot(_result["coins_sold"], color='r', label='Number of sell triggers')
        ax3.legend()
        ax3.grid()

    plt.xlim(xmin=-1, xmax=len(_result["net_profit"]))


def PlotOHLC(charts: Charts, trigger_queue=None,
             extra_plot1=None,
             extra_plot2=None,
             chart_style='ohlc',
             fast_ema=None,
             normal_ema=None,
             slow_ema=None,
             plot_bb=False, bb_sample_num=50, sigma=2,
             rsi=None,
             plot_obv=False,
             plot_volume=False):

    """arrange subplots"""
    if rsi and (plot_obv or plot_volume):
        big_rowspan = 70
        small_rowspan = 15
        rsi_pos = big_rowspan
        obv_pos = rsi_pos + small_rowspan
    elif rsi or plot_obv or plot_volume:
        big_rowspan = 80
        small_rowspan = 20
        rsi_pos = big_rowspan
        obv_pos = big_rowspan
    else:
        big_rowspan = 100
        small_rowspan = 0
        rsi_pos = big_rowspan
        obv_pos = big_rowspan

    if trigger_queue:
        triggers = ConvertTriggersForPlot(charts, trigger_queue)
    else:
        triggers = None

    for market_name in charts.close:
        """add figure number"""
        global TEST_GLOBAL_plt_fig_num
        TEST_GLOBAL_plt_fig_num += 1
        plt.figure(TEST_GLOBAL_plt_fig_num)
        # plt.get_current_fig_manager().full_screen_toggle()

        """do the plotting"""
        ax1 = plt.subplot2grid((100, 1), (0, 0), rowspan=big_rowspan, colspan=1)
        # ax1.set_facecolor('#4B4B4B')
        # plt.xticks(np.arange(charts.chart_lengths[market_name]), charts.date_unix[market_name], rotation=15)  # not showing the value of x bottom right
        # plt.locator_params(axis='x', nbins=6)  # shows only the original lines when chart is zoomed

        if fast_ema:
            ax1.plot(EMA_rolling(charts.close[market_name], window=fast_ema), color='C0', label=str(fast_ema) + ' EMA', alpha=.7)
        if normal_ema:
            ax1.plot(EMA_rolling(charts.close[market_name], window=normal_ema), color='gold', label=str(normal_ema) + ' EMA', alpha=.7)
        if slow_ema:
            ax1.plot(EMA_rolling(charts.close[market_name], window=slow_ema), color='red', label=str(slow_ema) + ' EMA', alpha=.7)
        if plot_bb:
            bb = BolingerBands_rolling(SMA_rolling(charts.close[market_name], window=bb_sample_num), StandardDev_rolling(charts.close[market_name], window=bb_sample_num), sigma=sigma)
            ax1.plot(bb["Upper"], color='purple', label='BB (' + str(bb_sample_num) + ', ' + str(sigma) + ')', alpha=.7)
            ax1.plot(bb["Lower"], color='purple', alpha=.7)
        if trigger_queue:
            ax1.plot(triggers["buy"][market_name], color='darkgreen', marker='^', linestyle='', alpha=.8)
            ax1.plot(triggers["sell"][market_name], color='darkred', marker='v', linestyle='', alpha=.8)
        if extra_plot1:
            dimensions = np.shape(extra_plot1[market_name])[0]
            if dimensions:
                for layer in range(0, dimensions):
                    ax1.plot(extra_plot1[market_name][layer], color='green')
            else:
                ax1.plot(extra_plot1[market_name], color='green')
        if extra_plot2:
            dimensions = np.shape(extra_plot2[market_name])[0]
            if dimensions:
                for layer in range(0, dimensions):
                    ax1.plot(extra_plot2[market_name][layer], color='red')
            else:
                ax1.plot(extra_plot2[market_name], color='red')

        if 'ohlc' == chart_style:
            candlestick2_ohlc(ax1,
                              opens=list(charts.open[market_name]),
                              highs=list(charts.high[market_name]),
                              lows=list(charts.low[market_name]),
                              closes=list(charts.close[market_name]),
                              colorup='#14E3C5',
                              colordown='#F45A5A',
                              width=1,
                              alpha=1.0
                              )
        else:  # 'line' == chart_style
            ax1.plot(charts.close[market_name], color='green')

        ax1.grid(True)
        ax1.set_title(market_name)
        ax1.set_ylabel('Price')
        if fast_ema or normal_ema or slow_ema or plot_bb:
            ax1.legend()

        if rsi:
            ax2 = plt.subplot2grid((100, 1), (rsi_pos, 0), sharex=ax1, rowspan=small_rowspan, colspan=1)

            rsi_line = RSI_rolling(charts.close[market_name], window=rsi)
            ax2.plot(rsi_line, color='C0')
            ax2.axhline(y=70, color='red', linestyle='--', alpha=.5)
            ax2.axhline(y=30, color='green', linestyle='--', alpha=.6)
            ax2.set_ylim(bottom=0, top=100)
            ax2.set_ylabel(str(rsi) + ' RSI')
            ax2.set_yticks([30, 70])
            ax2.xaxis.grid()
            # plt.connect('button_press_event', DrawVerticalLine)

        if plot_obv or plot_volume:
            ax3 = plt.subplot2grid((100, 1), (obv_pos, 0), sharex=ax1, rowspan=small_rowspan, colspan=1)

            if plot_volume:
                if not plot_obv:
                    ax3_vol = ax3
                else:
                    ax3_vol = ax3.twinx()
                volume_overlay(ax3_vol, charts.open[market_name], charts.close[market_name], charts.volume[market_name],
                               colorup='#14E3C5', colordown='#F45A5A', width=1, alpha=.6)
                ax3_vol.set_ylim(0, max(charts.volume[market_name]))
                ax3_vol.set_ylabel('Volume')
                ax3_vol.get_yaxis().set_label_position('left')
                ax3_vol.get_yaxis().tick_left()

            if plot_obv:
                obv = OBV_rolling(charts, market_name)
                ax3.plot(obv, color='darkblue', label='OBV')
                ax3.set_ylim(bottom=min(obv), top=max(obv))
                ax3.legend()
                ax3.get_yaxis().set_ticks([])
                ax3.xaxis.grid()

        plt.xlim(xmin=-1, xmax=charts.chart_lengths[market_name] + 1)
