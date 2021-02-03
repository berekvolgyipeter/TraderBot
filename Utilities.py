from Configuration.DirectoryLocations import PROJECT_LOCATION
from Configuration.Parameters import REFRESH_PERIODICITY, BASE_CURRENCY, BASE_CURRENCY_LEN
import datetime


class Data:
    def __init__(self):
        self.last = dict()
        self.bid = dict()
        self.ask = dict()

        self.open = dict()
        self.high = dict()
        self.low = dict()
        self.close = dict()

        self.volume = dict()
        self.base_volume = dict()

        self.validity = dict()
        self.min_trade_size = dict()


class TriggerQueue:
    def __init__(self):
        self.buy = []
        self.sell = []
        self.invalidity_sell = []


def LogOutput(message: str):
    print(message)
    text_file = open(PROJECT_LOCATION + "Log/Output.txt", "a")
    text_file.write(message + '\n')
    text_file.close()


def DailyTrigger(start_date):
    """This function gives a trigger once a day"""
    ret = False
    now = datetime.datetime.now()
    if start_date.time() <= now.time() <= \
       (start_date + datetime.timedelta(seconds=int(REFRESH_PERIODICITY * 0.95))).time():
        ret = True
    return ret


def GetTopVolumeCoins(charts: Data, number_of_coins=30):
    """Returns the top n 24h volume coins as market name"""
    top_str = []
    top_volume = []
    for market_name in charts.base_volume:
        if BASE_CURRENCY == market_name[:BASE_CURRENCY_LEN]:
            volume_in_base_currency = charts.base_volume[market_name][-1]
            if len(top_volume) < number_of_coins:
                top_volume.append(volume_in_base_currency)
                top_str.append(market_name)
            else:
                min_top_volume = min(top_volume)
                if volume_in_base_currency > min_top_volume:
                    index_min_top_volume = top_volume.index(min_top_volume)
                    del (top_str[index_min_top_volume])
                    del (top_volume[index_min_top_volume])
                    top_volume.append(volume_in_base_currency)
                    top_str.append(market_name)

    LogOutput(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +
              ": Top 24h volume coins have been selected for trading: " + str(top_str))
    return top_str


def GetCoinsWithGivenMinVolume(charts: Data, min_base_volume=15):
    """Returns those market names which had at least
    'min_base_volume' base volume in the last 24 hours"""
    selected_markets = []
    for market_name in charts.base_volume:
        if BASE_CURRENCY == market_name[:BASE_CURRENCY_LEN]:
            volume_in_base_currency = charts.base_volume[market_name][-1]
            if volume_in_base_currency > min_base_volume:
                selected_markets.append(market_name)

    LogOutput(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +
              ": Markets which had at least " + str(min_base_volume) + " " + BASE_CURRENCY +
              " base volume in the last 24 hours have been selected for trading: " + str(selected_markets))
    return selected_markets
