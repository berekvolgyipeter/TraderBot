from datetime import datetime
from Bittrex import Bittrex
from Configuration.Keys import *
from Configuration.Parameters import *
from Configuration.DirectoryLocations import *
from ApiManager import ExecuteApiCall
from Utilities import TriggerQueue, LogOutput
import csv


class OrderManager:

    def __init__(self):
        self.__api = Bittrex(API_KEY, API_SECRET)

    def GetBalances(self):
        """
        Returns the account balances for each currency

        output structure:
        ret["<currency name>"] refers to a float number
        """
        ret = dict()
        balances = ExecuteApiCall(self.__api.get_balances())
        if balances["success"]:
            for result in balances["result"]:
                ret[result["Currency"]] = result["Available"]
        return ret

    def Buy(self, market_name, amount_to_buy, rate):
        """Places a limit buy order on the selected market"""
        base_currency_balance = ExecuteApiCall(self.__api.get_balance(BASE_CURRENCY))
        buy = {"success": False}
        if (base_currency_balance["success"]) and \
           (base_currency_balance["result"]["Available"] >= amount_to_buy * rate):
            buy = ExecuteApiCall(self.__api.buy_limit(market_name, amount_to_buy, rate))
        return buy

    def Sell(self, market_name, rate, amount_to_sell):
        """Places a limit sell order on the selected market"""
        sell = {"success": False}
        if amount_to_sell * rate >= MIN_SELL_SIZE:
            sell = ExecuteApiCall(self.__api.sell_limit(market_name, amount_to_sell, rate))
        return sell

    @staticmethod
    def GetBuyRate(ticker):
        """Calculates a buy rate for a selected ticker based on the spread between last and ask prices"""
        if ticker["result"]["Ask"] / ticker["result"]["Last"] >= BID_COEFFICIENT:
            rate = ticker["result"]["Last"] * BID_COEFFICIENT
        else:
            rate = ticker["result"]["Ask"]
        return rate

    @staticmethod
    def GetSellRate(ticker):
        """Calculates a sell rate for a selected ticker based on the spread between last and bid prices"""
        if ticker["result"]["Bid"] / ticker["result"]["Last"] <= ASK_COEFFICIENT:
            rate = ticker["result"]["Last"] * ASK_COEFFICIENT
        else:
            rate = ticker["result"]["Bid"]
        return rate

    def RefreshPendingOrders(self):
        """Refreshes pending orders: this function makes limit orders behave as market orders"""
        open_orders = ExecuteApiCall(self.__api.get_open_orders())
        refreshed_orders = []
        if open_orders["success"]:
            for order in open_orders["result"]:
                market_name = order["Exchange"]
                ticker = ExecuteApiCall(self.__api.get_ticker(market_name))

                if ticker["success"]:
                    if "LIMIT_BUY" == order["OrderType"]:
                        filled_quantity = order["Quantity"] - order["QuantityRemaining"]
                        """Only cancel buy orders if the filled quantity is greater than MIN_ORDER_SIZE"""
                        if (0.0 == filled_quantity) or (MIN_ORDER_SIZE < (filled_quantity * ticker["result"]["Last"])):
                            cancelled_order = ExecuteApiCall(self.__api.cancel(order["OrderUuid"]))
                            if cancelled_order["success"]:
                                rate = self.GetBuyRate(ticker)
                                buy = self.Buy(market_name, order["QuantityRemaining"], rate)
                                if buy["success"]:
                                    refreshed_orders.append("buy-" + market_name)

                    elif "LIMIT_SELL" == order["OrderType"]:
                        """Only cancel sell orders if the remaining quantity is greater than MIN_ORDER_SIZE"""
                        if MIN_ORDER_SIZE < (order["QuantityRemaining"] * ticker["result"]["Last"]):
                            cancelled_order = ExecuteApiCall(self.__api.cancel(order["OrderUuid"]))
                            if cancelled_order["success"]:
                                rate = self.GetSellRate(ticker)
                                balance = ExecuteApiCall(self.__api.get_balance(market_name[BASE_CURRENCY_LEN + 1:]))
                                if balance["success"]:
                                    sell = self.Sell(market_name, rate, balance["result"]["Balance"])
                                    if sell["success"]:
                                        refreshed_orders.append("sell-" + market_name)
        return refreshed_orders

    def CancelOpenOrdersAtTrigger(self, market_name):
        """
        This function cancels all open orders for the selected market
        if the amount of money involved is above MIN_ORDER_SIZE.
        """
        open_orders = ExecuteApiCall(self.__api.get_open_orders(market_name))
        cancelled_orders = []
        if open_orders["success"]:
            for order in open_orders["result"]:

                ticker = ExecuteApiCall(self.__api.get_ticker(market_name))

                if ticker["success"]:
                    if "LIMIT_BUY" == order["OrderType"]:
                        filled_quantity = order["Quantity"] - order["QuantityRemaining"]
                        """Only cancel buy orders if the filled quantity is greater than MIN_ORDER_SIZE"""
                        if (0.0 == filled_quantity) or (MIN_ORDER_SIZE < (filled_quantity * ticker["result"]["Last"])):
                            cancelled_order = ExecuteApiCall(self.__api.cancel(order["OrderUuid"]))
                            if cancelled_order["success"]:
                                cancelled_orders.append("buy-" + market_name)

                    elif "LIMIT_SELL" == order["OrderType"]:
                        """Only cancel sell orders if the remaining quantity is greater than 50K satoshis"""
                        if MIN_ORDER_SIZE < (order["QuantityRemaining"] * ticker["result"]["Last"]):
                            cancelled_order = ExecuteApiCall(self.__api.cancel(order["OrderUuid"]))
                            if cancelled_order["success"]:
                                cancelled_orders.append("sell-" + market_name)
        return cancelled_orders

    def CancelObsoleteOpenBuyOrders(self):
        """Cancel all open buy orders which are older than 'ORDER_TIMEOUT_MIN' """
        open_orders = ExecuteApiCall(self.__api.get_open_orders())
        cancelled_buy_orders_timeout = []
        if open_orders["success"]:
            for order in open_orders["result"]:
                try:
                    open_time = datetime.strptime(order["Opened"], '%Y-%m-%dT%H:%M:%S.%f')
                except ValueError:
                    open_time = datetime.strptime(order["Opened"], '%Y-%m-%dT%H:%M:%S')

                if (datetime.now() - open_time).seconds >= (ORDER_TIMEOUT_MIN * 60):  # TODO: check if times are in same time zone
                    if "LIMIT_BUY" == order["OrderType"]:
                        ticker = ExecuteApiCall(self.__api.get_ticker(order["Exchange"]))
                        if ticker["success"]:
                            filled_quantity = order["Quantity"] - order["QuantityRemaining"]
                            """Only cancel buy orders if the filled quantity is greater than MIN_ORDER_SIZE"""
                            if (0.0 == filled_quantity) or \
                               (MIN_ORDER_SIZE < (filled_quantity * ticker["result"]["Last"])):
                                cancelled_order = ExecuteApiCall(self.__api.cancel(order["OrderUuid"]))
                                if cancelled_order["success"]:
                                    cancelled_buy_orders_timeout.append(order["Exchange"])
        return cancelled_buy_orders_timeout

    def Run(self, trigger_queue: TriggerQueue):
        """
        This is the main function, it is called periodically.
        It places and logs buy and sell orders at triggers and refreshes pending orders.
        """
        buy_orders = []
        sell_orders = []
        invalidity_sell_orders = []
        cancelled_orders = []
        # refreshed_orders = []
        buy_triggers = []
        sell_triggers = []

        """Refreshing orders"""
        refreshed_orders = self.RefreshPendingOrders()

        """Calculating position size"""
        base_currency_balance = ExecuteApiCall(self.__api.get_balance(BASE_CURRENCY))
        if base_currency_balance["success"]:
            position_size = base_currency_balance["result"]["Available"] * POSITION_SIZE_COEFFICIENT / NUM_OF_POSITIONS
            if position_size > MAX_POSITION_SIZE:
                position_size = MAX_POSITION_SIZE
            elif position_size < MIN_POSITION_SIZE:
                position_size = MIN_POSITION_SIZE
        else:
            position_size = MIN_POSITION_SIZE

        """Creating new list without redundant triggers"""
        for market_name in trigger_queue.buy:
            if market_name not in buy_triggers:
                buy_triggers.append(market_name)

        """Placing buy orders"""
        for market_name in buy_triggers:
            ticker = ExecuteApiCall(self.__api.get_ticker(market_name))
            if ticker["success"]:
                cancel = self.CancelOpenOrdersAtTrigger(market_name)
                if cancel:
                    cancelled_orders.append(cancel)
                rate = self.GetBuyRate(ticker)
                amount_to_buy = position_size / rate
                buy = self.Buy(market_name, amount_to_buy, rate)
                if buy["success"]:
                    buy_orders.append(market_name)
                    buy_triggers.remove(market_name)

        """Creating new list without redundant triggers"""
        for market_name in trigger_queue.sell:
            if market_name not in sell_triggers:
                sell_triggers.append(market_name)

        """Placing sell orders"""
        balances = self.GetBalances()
        for coin in balances:
            if balances[coin] > 0.0:
                market_name = BASE_CURRENCY + "-" + coin
                if market_name in sell_triggers:
                    ticker = ExecuteApiCall(self.__api.get_ticker(market_name))
                    if ticker["success"]:
                        cancel = self.CancelOpenOrdersAtTrigger(market_name)
                        if cancel:
                            cancelled_orders.append(cancel)
                        rate = self.GetSellRate(ticker)
                        sell = self.Sell(market_name, rate, balances[coin])
                        if sell["success"]:
                            sell_orders.append(market_name)
                            sell_triggers.remove(market_name)
                            if market_name in trigger_queue.invalidity_sell:
                                invalidity_sell_orders.append(market_name)

        """Log the orders to file"""
        date = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4])
        with open(PROJECT_LOCATION + "Log/Orders.csv", 'a', newline='') as csvfile:
            logfilewriter = csv.writer(csvfile)
            logfilewriter.writerow([date])
            logfilewriter.writerow(['Cancelled orders: ' + str(cancelled_orders)])
            logfilewriter.writerow(['Refreshed orders: ' + str(refreshed_orders)])
            logfilewriter.writerow(['Buy orders: ' + str(buy_orders)])
            logfilewriter.writerow(['Sell orders: ' + str(sell_orders)])
            logfilewriter.writerow(['Sell orders because of invalidity: ' + str(invalidity_sell_orders)])
            logfilewriter.writerow('\n')
        csvfile.close()

        """Log the orders to console"""
        if cancelled_orders:
            LogOutput(date + ': Cancelled orders: ' + str(cancelled_orders))
        if refreshed_orders:
            LogOutput(date + ': Refreshed orders: ' + str(refreshed_orders))
        if buy_orders:
            LogOutput(date + ': Buy orders: ' + str(buy_orders))
        if sell_orders:
            LogOutput(date + ': Sell orders: ' + str(sell_orders))
        if invalidity_sell_orders:
            LogOutput(date + ': Sell orders because of invalidity: ' + str(invalidity_sell_orders))
