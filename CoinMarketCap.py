import requests
from datetime import datetime
from Logging import LogOutput


def CoinMarketCapTopCoins(num):
    ret = []
    data = []
    try:
        data = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=' + str(num)).json()
    except Exception as ex:
        template = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +\
                   "An exception of type {0} occurred during the usage of a coinmarketcap API. Arguments: {1!r}"
        message = template.format(type(ex).__name__, ex.args)
        LogOutput(message)
        try:
            data = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=' + str(num)).json()
        except Exception as ex:
            template = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + \
                       "An exception of type {0} occurred during the usage of a coinmarketcap API. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            LogOutput(message)
            try:
                data = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=' + str(num)).json()
            except Exception as ex:
                template = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + \
                           "An exception of type {0} occurred during the usage of a coinmarketcap API. Arguments: {1!r}"
                message = template.format(type(ex).__name__, ex.args)
                LogOutput(message)

    for result in data:
        try:
            if 'BTC' != result['symbol']:
                if 'BCH' != result['symbol']:
                    ret.append(result['symbol'])
                else:
                    ret.append('BCC')
        except KeyError:
            LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + 'CoinMarketCap API key error.')
            pass

    return ret


def RequestSP100():
    response = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=101')
    data = response.json()
    market_cap_sum = 0.0
    sp_100 = 0.0
    for i in range(1, 101):
        market_cap_sum += float(data[i]['market_cap_usd'])
    for i in range(1, 101):
        weight = float(data[i]['market_cap_usd']) / market_cap_sum
        sp_100 += weight * float(data[i]['price_btc'])
    return sp_100


def GetSP100():
    ret = -1.0
    try:
        ret = RequestSP100()
    except Exception as ex:
        template = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +\
                   "An exception of type {0} occurred during the usage of a coinmarketcap API. Arguments: {1!r}"
        message = template.format(type(ex).__name__, ex.args)
        LogOutput(message)
        try:
            ret = RequestSP100()
        except Exception as ex:
            template = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + \
                       "An exception of type {0} occurred during the usage of a coinmarketcap API. Arguments: {1!r}"
            message = template.format(type(ex).__name__, ex.args)
            LogOutput(message)
            try:
                ret = RequestSP100()
            except Exception as ex:
                template = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + \
                           "An exception of type {0} occurred during the usage of a coinmarketcap API. Arguments: {1!r}"
                message = template.format(type(ex).__name__, ex.args)
                LogOutput(message)
                LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +
                          "SP100 is returned with an invalid value (-1.0).")

    return ret
