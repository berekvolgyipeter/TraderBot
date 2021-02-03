from Configuration.TestParameters import *
from Configuration.Parameters import *
from Utilities import *
from ApiManager import ExecuteApiCall
from Bittrex import Bittrex
from datetime import datetime


class TestOrderManager:
    def __init__(self):
        self.__api = Bittrex('', '')
        self.__balances = dict()
        self.__base_currency_balance = TEST_INITIAL_BALANCE
        self.__position_size = TEST_INITIAL_BALANCE / TEST_NUM_OF_POSITIONS

    def Buy(self, market_name, rate):
        ret = False
        coin = market_name[BASE_CURRENCY_LEN + 1:]
        """If the base currency balance is enough, perform the exchange"""
        if self.__base_currency_balance >= self.__position_size:
            self.__base_currency_balance -= self.__position_size
            self.__balances[coin] += self.__position_size * FEE_COEFFICIENT / rate
            ret = True
        return ret

    def Sell(self, market_name, rate):
        ret = False
        coin = market_name[BASE_CURRENCY_LEN + 1:]
        """If there is a balance of the selected coin, sell all"""
        if self.__balances[coin] > 0.0:
            self.__base_currency_balance += self.__balances[coin] * FEE_COEFFICIENT * rate
            self.__balances[coin] = 0.0
            ret = True
        return ret

    @staticmethod
    def GetBuyRate(ticker):
        """Calculates a buy rate for a selected ticker based on the spread between last and ask prices"""
        if ticker["result"]["Ask"] > ticker["result"]["Last"] * BID_COEFFICIENT:
            rate = ticker["result"]["Last"] * BID_COEFFICIENT
        else:
            rate = ticker["result"]["Ask"]
        return rate

    @staticmethod
    def GetSellRate(ticker):
        """Calculates a sell rate for a selected ticker based on the spread between last and bid prices"""
        if ticker["result"]["Bid"] < ticker["result"]["Last"] * ASK_COEFFICIENT:
            rate = ticker["result"]["Last"] * ASK_COEFFICIENT
        else:
            rate = ticker["result"]["Bid"]
        return rate

    def CalculateBalanceAll(self, charts: Data):
        """Calculates the sum of all balances converted to base currency at actual rate"""
        balance_all = self.__base_currency_balance
        for coin in self.__balances:
            balance_all += self.__balances[coin] * FEE_COEFFICIENT * \
                             charts.last[BASE_CURRENCY + '-' + coin][-1] * ASK_COEFFICIENT
        return balance_all

    def Run(self, trigger_queue: TriggerQueue, charts: Data):
        """
        This is the main function, it is called periodically.
        It places buy and sell simulated orders at triggers, and logs them.
        """
        buy_orders = []
        sell_orders = []
        invalidity_sell_orders = []
        buy_triggers = []
        sell_triggers = []

        """Init balances"""
        for market_name in charts.last:
            coin = market_name[BASE_CURRENCY_LEN + 1:]
            if coin not in self.__balances:
                self.__balances[coin] = 0.0

        """Calculating position size"""
        self.__position_size = self.__base_currency_balance * POSITION_SIZE_COEFFICIENT / TEST_NUM_OF_POSITIONS
        if self.__position_size > TEST_MAX_POSITION_SIZE:
            self.__position_size = TEST_MAX_POSITION_SIZE
        elif self.__position_size < TEST_MIN_POSITION_SIZE:
            self.__position_size = TEST_MIN_POSITION_SIZE

        """Creating new list without redundant triggers"""
        for market_name in trigger_queue.buy:
            if market_name not in buy_triggers:
                buy_triggers.append(market_name)

        """Placing buy orders"""
        for market_name in buy_triggers:
            ticker = ExecuteApiCall(self.__api.get_ticker(market_name))
            if ticker["success"]:
                rate = self.GetBuyRate(ticker)
                buy = self.Buy(market_name, rate)
                if buy:
                    buy_orders.append(market_name)


        """Creating new list without redundant triggers"""
        for market_name in trigger_queue.sell:
            if market_name not in sell_triggers:
                sell_triggers.append(market_name)

        """Placing sell orders"""
        for market_name in sell_triggers:
            coin = market_name[BASE_CURRENCY_LEN + 1:]
            if self.__balances[coin] > 0.0:
                ticker = ExecuteApiCall(self.__api.get_ticker(market_name))
                if ticker["success"]:
                    rate = self.GetSellRate(ticker)
                    sell = self.Sell(market_name, rate)
                    if sell:
                        sell_orders.append(market_name)
                        if market_name in trigger_queue.invalidity_sell:
                            invalidity_sell_orders.append(market_name)

        """Log the orders to console"""
        date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4])
        if buy_orders:
            LogOutput(date + ': Buy orders: ' + str(buy_orders))
        if sell_orders:
            LogOutput(date + ': Sell orders: ' + str(sell_orders))
        if invalidity_sell_orders:
            LogOutput(date + ': Sell orders because of invalidity: ' + str(invalidity_sell_orders))

        LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) +
                  ': ' + BASE_CURRENCY + ' balance: ' + str(format(self.__base_currency_balance, '.6f')) +
                  ', Full balance in ' + BASE_CURRENCY + ': ' + str(format(self.CalculateBalanceAll(charts), '.6f')) +
                  '\n')
