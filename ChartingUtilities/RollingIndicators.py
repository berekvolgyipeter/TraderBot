from math import sqrt
import pandas as pd
import numpy as np
from HistoricDataHandler.PriceChartHistory import Charts


def EMA_rolling(chart, window=20):
    """Exponential Moving Average"""
    ema = [np.average(chart[0:window])]
    cutoff = 2.0 / (window + 1)
    for k in range(window, len(chart)):
        """(last_sample - last_ema) * cutoff + last_ema"""
        ema.append((chart[k] - ema[k-window]) * cutoff + ema[k-window])
    return np.concatenate((np.full(window - 1, float('nan')), np.asarray(ema)))


def SMA_rolling(chart, window=20, nans_in_chart=False):
    if nans_in_chart:
        chart[0:window-1] = np.full(window-1, chart[window])
    ret = np.cumsum(chart, dtype=float)
    ret[window:] = ret[window:] - ret[:-window]
    return np.concatenate((np.full(window - 1, float('nan')), (ret[window - 1:] / window)))


def StandardDev_rolling(chart, window=20):
    df = pd.DataFrame({'price': chart})
    return df['price'].rolling(window).std().values


def BolingerBands_rolling(rolling_mean, rolling_std, sigma=2):
    bolinger_bands = {'Upper': rolling_mean + sigma * rolling_std,
                      'Lower': rolling_mean - sigma * rolling_std}
    return bolinger_bands


def RSI_rolling(chart, window=14):
    """
    RSI = 100 - 100 / (1 + RS)

    Where RS = Average gain of up periods during the specified time frame /
               Average loss of down periods during the specified time frame/

    The RSI provides a relative evaluation of the strength of a security's recent price performance,
    thus making it a momentum indicator.
    RSI values range from 0 to 100.
    The default time frame for comparing up periods to down periods is 14, as in 14 trading days.

    Read more: Relative Strength Index (RSI) https://www.investopedia.com/terms/r/rsi.asp#ixzz5AsTBcWjg
    """
    deltas = np.diff(chart)
    seed = deltas[:window+1]
    up = seed[seed >= 0].sum()/window
    down = -seed[seed < 0].sum()/window
    rs = up/down
    rsi = np.zeros_like(chart)
    rsi[:window] = 100. - 100./(1.+rs)

    for i in range(window, len(chart)):
        delta = deltas[i-1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(window-1) + upval)/window
        down = (down*(window-1) + downval)/window

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi


def MACD_rolling(fast_ma, slow_ma, n=1):
    return np.concatenate((np.full(n, float('nan')), np.diff((fast_ma - slow_ma), n)))


def OBV_rolling(chart: Charts, market_name):
    obv = np.zeros(chart.chart_lengths[market_name])
    obv[0] = chart.base_volume[market_name][0]
    for i in range(1, chart.chart_lengths[market_name]):
        if chart.close[market_name][i] > chart.close[market_name][i-1]:
            obv[i] = obv[i-1] + chart.base_volume[market_name][i]
        elif chart.close[market_name][i] < chart.close[market_name][i-1]:
            obv[i] = obv[i - 1] - chart.base_volume[market_name][i]
        else:
            obv[i] = obv[i - 1]
    return obv


def RollingStochasticOscillator(chart: Charts, market_name, fast_k=5, full_k=3, d=3, res=20):
    """


    Full K% or K% slows down Fast K% with a Simple Moving Average (SMA).
    Full D% or D% adds a second smoothing average.
    Lower Fast K%, K% and D% variables =  a shorter-term lookback period with less smoothing
    Higher Fast K%, K% and D% variables = a longer-term lookback period with greater smoothing
    """
    df = pd.DataFrame({'high': chart.high[market_name],
                       'low': chart.low[market_name],
                       'close': chart.close[market_name]})  # creating pandas data frame

    high = df['high'].rolling(fast_k * res).max().as_matrix()
    low = df['low'].rolling(fast_k * res).min().as_matrix()
    raw_k = np.nan_to_num(100 * (df['close'] - low) / (high - low))
    percent_k = np.nan_to_num(SMA_rolling(raw_k, window=full_k * res, nans_in_chart=False))
    percent_d = np.nan_to_num(SMA_rolling(percent_k, window=d * res, nans_in_chart=False))

    return percent_k, percent_d


def RollingReturn(chart, window=1):
    length = len(chart)
    ret = np.full(length, float('nan'))
    for i in range(window, length):
        ret[i] = (chart[i] - chart[i - window]) / chart[i]
    return ret


def RollingVolatility(rolling_returns_per_sample, window=20):
    return StandardDev_rolling(rolling_returns_per_sample, window=window)


def RollingSharpeRatio(returns_per_sample, window=30 * 20):
    """Assumption: risk free daily return is 0%"""
    ret = sqrt(window) * \
          SMA_rolling(returns_per_sample[1:], window=window) / StandardDev_rolling(returns_per_sample[1:], window=window)
    return np.concatenate((np.full(1, float('nan')), ret))
