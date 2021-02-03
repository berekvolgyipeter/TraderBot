from Bittrex import Bittrex
from Configuration.Keys import *
from Configuration.Parameters import *
from Configuration.DirectoryLocations import *
from ApiManager import ExecuteApiCall
from Utilities import LogOutput
from datetime import datetime
import csv


class Logging:
    """This class logs profit"""
    def __init__(self):
        self.__api = Bittrex(API_KEY, API_SECRET)

    def Run(self, price_charts):
        balances = ExecuteApiCall(self.__api.get_balances())
        balance_all = 0.0  # sum of all balances converted to base currency
        base_currency_balance = 0.0  # actual balance of base currency

        if balances["success"]:

            """Filling log balances"""
            for result in balances["result"]:
                market_name = BASE_CURRENCY + '-' + result["Currency"]
                if BASE_CURRENCY == result["Currency"]:
                    balance_all += result["Balance"]
                    base_currency_balance = result["Balance"]
                elif (result["Balance"] > 0.0) and \
                     (market_name in price_charts) and (price_charts[market_name][-1] > 0.0):
                    balance_all += result["Balance"] * price_charts[market_name][-1] \
                                   * ASK_COEFFICIENT * FEE_COEFFICIENT

            with open(PROJECT_LOCATION + "Log/Logging.csv", 'a', newline='') as csvfile:
                logfilewriter = csv.writer(csvfile)
                logfilewriter.writerow([str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]),
                                        " Full balance in " + BASE_CURRENCY + ": " + str(format(balance_all, '.6f'))])
                logfilewriter.writerow([BASE_CURRENCY + ' balance: ' + str(format(base_currency_balance, '.6f'))])
                logfilewriter.writerow('\n')
            csvfile.close()

            LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +
                      ': ' + BASE_CURRENCY + ' balance: ' + str(format(base_currency_balance, '.6f')) +
                      ', Full balance in ' + BASE_CURRENCY + ': ' + str(format(balance_all, '.6f')) + '\n')
