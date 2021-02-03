import csv
import requests
import datetime
import time
from Configuration.DirectoryLocations import CHARTS_LOCATION
from Configuration.TestParameters import POLONIEX_USDT_MARKETS, POLONIEX_BTC_MARKETS

LOCATION = CHARTS_LOCATION + "/poloniex/fresh_data_by_api_call/"


"""
returnChartData:
Returns candlestick chart data. 
Required GET parameters are:
"currencyPair", "period" 
                                                5m    15m   30m   2h    4h         1d
(candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400),
"start", and "end". 
"Start" and "end" are given in UNIX timestamp format and used to specify the date range for the data returned. 

Sample output:

[{"date":1405699200,"high":0.0045388,"low":0.00403001,"open":0.00404545,"close":0.00427592,"volume":44.11655644,
"quoteVolume":10259.29079097,"weightedAverage":0.00430015}, ...]

date refers to the open time of the candlestick
"""


"""                                y,   m, d, h, m """
start = str(int(datetime.datetime(2017, 1, 1, 0, 0).timestamp()))
end = str(int(datetime.datetime(2019, 10, 5, 0, 0).timestamp()))
period = '86400'

markets = POLONIEX_USDT_MARKETS
#markets = POLONIEX_BTC_MARKETS
#markets = POLONIEX_USDT_MARKETS + POLONIEX_BTC_MARKETS


for market in markets:
    list_date = []  # open date in '%Y.%m.%d %H:%M:%S' format
    list_date_unix = []  # open UTC date for this candle in milliseconds since the Unix epoch.
    list_open = []
    list_high = []
    list_low = []
    list_close = []
    list_volume = []  # total amount of this asset transacted within this candle.
    list_base_volume = []  # total amount of base currency transacted for this asset within this candle.

    print("Getting price chart data of " + str(market) + "...")

    url = 'https://poloniex.com/public?command=returnChartData&currencyPair=' + str(market) + \
          '&start=' + start + '&end=' + end + '&period=' + period

    response = requests.get(url)
    data = response.json()

    for d in data:
        list_date.append(time.strftime('%Y.%m.%d %H:%M:%S', time.gmtime(int(d['date']))))
        list_date_unix.append((int(d['date'])))
        list_open.append(format(d['open'], '.8f'))
        list_high.append(format(d['high'], '.8f'))
        list_low.append(format(d['low'], '.8f'))
        list_close.append(format(d['close'], '.8f'))
        list_volume.append(format(d['quoteVolume'], '.8f'))  # poloniex interprets quoteVolume as the total amount of the quote exchanged
        list_base_volume.append(format(d['volume'], '.8f'))  # poloniex interprets volume as base volume

    with open(LOCATION + market + '.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for j in range(0, len(list_date)):
            writer.writerow([str(list_date[j]), str(list_date_unix[j]),
                            str(list_open[j]), str(list_high[j]), str(list_low[j]), str(list_close[j]),
                            str(list_volume[j]), str(list_base_volume[j])])
    csvfile.close()

print("\nChart data has been downloaded successfully!")
