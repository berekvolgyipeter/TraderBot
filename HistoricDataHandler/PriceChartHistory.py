import csv
import os
import numpy as np
import time
from Configuration.DirectoryLocations import CHARTS_LOCATION_POLONIEX


class Charts:
    def __init__(self):
        self.date = dict()
        self.date_unix = dict()
        self.open = dict()
        self.high = dict()
        self.low = dict()
        self.close = dict()
        self.volume = dict()
        self.base_volume = dict()
        self.min_date_unix = int(time.time())  # Setting it to current time in unix time stamp
        self.max_date_unix = 0
        self.chart_lengths = dict()
        self.max_len = 0
        self.max_len_market = ''
        self.broker = 'POLONIEX'
        self.resolution_min = 0  # time span of a candle in minutes


def DoReading(path, fname):
    """Reads one price chart file"""

    ret = Charts()  # TODO: think this declaration over

    _date = []
    _date_unix = []
    _open = []
    _high = []
    _low = []
    _close = []
    _volume = []
    _base_volume = []
    _broker = ''

    with open(path + fname, "r", ) as priceChartFile:
        price_chart_file_reader = csv.reader(priceChartFile)

        if "poloniex" in path:
            for row in price_chart_file_reader:
                if len(row) > 0:
                    _date.append(str(row[0]))
                    _date_unix.append(int(row[1]))
                    _open.append(float(row[2]))
                    _high.append(float(row[3]))
                    _low.append(float(row[4]))
                    _close.append(float(row[5]))
                    _volume.append(float(row[6]))
                    _base_volume.append(float(row[7]))
            _broker = 'POLONIEX'

        priceChartFile.close()

    ret.date = np.asarray(_date)
    ret.date_unix = np.asarray(_date_unix)
    ret.open = np.asarray(_open)
    ret.high = np.asarray(_high)
    ret.low = np.asarray(_low)
    ret.close = np.asarray(_close)
    ret.volume = np.asarray(_volume)
    ret.base_volume = np.asarray(_base_volume)
    ret.broker = _broker

    return ret


def ReadPriceCharts(path, base_currency='USDT', read_these_charts=None):
    """Reads the selected price chart files with the selected base currency"""

    charts = Charts()

    if read_these_charts:
        print("Fetching data from " + path + "... base currency: " + base_currency + ", reading charts: " + str(read_these_charts))
    else:
        print("Fetching data from " + path + "... base currency: " + base_currency + ", reading charts: all")

    for fname in os.listdir(path):
        data = None
        if fname[0:len(base_currency)] == base_currency:
            if read_these_charts:
                if fname[0:-4] in read_these_charts:
                    data = DoReading(path, fname)
            else:
                data = DoReading(path, fname)

        if data:
            market_name = fname.replace('.csv', '')

            charts.date[market_name] = data.date
            charts.date_unix[market_name] = data.date_unix
            charts.open[market_name] = data.open
            charts.high[market_name] = data.high
            charts.low[market_name] = data.low
            charts.close[market_name] = data.close
            charts.volume[market_name] = data.volume
            charts.base_volume[market_name] = data.base_volume
            charts.chart_lengths[market_name] = len(charts.close[market_name])
            charts.broker = data.broker  # TODO: this is not optimal

    for market_name in charts.close:
        if charts.date_unix[market_name][0] < charts.min_date_unix:
            charts.min_date_unix = charts.date_unix[market_name][0]
        if charts.date_unix[market_name][-1] > charts.max_date_unix:
            charts.max_date_unix = charts.date_unix[market_name][-1]
        if len(charts.close[market_name]) > charts.max_len:
            charts.max_len = len(charts.close[market_name])
            charts.max_len_market = market_name

    print("Data is now ready to use.")

    return charts


def GetChartData(broker='POLONIEX', get_data_from='saved_data',
                 year='from_2017', resolution='1d', base_currency='USDT', read_these_charts=None):
    """Configurable price chart reader function"""

    if 'POLONIEX' == broker:
        if 'saved_data' == get_data_from:
            path = CHARTS_LOCATION_POLONIEX + year + "/" + resolution + "/"
        else:  # 'fresh_data_by_api_call' == get_data_from:
            path = CHARTS_LOCATION_POLONIEX + "fresh_data_by_api_call/"
    else:
        path = CHARTS_LOCATION_POLONIEX + "fresh_data_by_api_call/"

    charts = ReadPriceCharts(path=path, base_currency=base_currency, read_these_charts=read_these_charts)
    if '5m' == resolution:
        charts.resolution_min = 5
    elif '15m' == resolution:
        charts.resolution_min = 15
    elif '30m' == resolution:
        charts.resolution_min = 30
    elif '2h' == resolution:
        charts.resolution_min = 120
    elif '4h' == resolution:
        charts.resolution_min = 240
    elif '1d' == resolution:
        charts.resolution_min = 1440
    else:
        pass

    return charts
