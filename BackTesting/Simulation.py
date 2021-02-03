from Configuration.TestParameters import *
from Configuration.Parameters import *
import numpy as np
from HistoricDataHandler.PriceChartHistory import Charts
from BackTesting.TestUtilities import Position, CalculateChartIndex, IsChartIndexInRange, TriggerQueue


class Simulation:

    def __init__(self, charts: Charts):
        """dictionary for storing the available balances for all coins"""
        self.balances = dict()
        for market_name in charts.close:
            self.balances[market_name] = 0.0
        """base currency balance"""
        self.base_balance = TEST_INITIAL_BALANCE

        """
        data structure:
        ['BTC_ETH'][<price in base currency>][<bid price>]
        """
        self.buy_orders = dict()
        """
         data structure:
         ['BTC_ETH'][<balance in ETH>][<ask price>]
         """
        self.sell_orders = dict()

        self.positions = dict()
        for market_name in charts.close:
            self.positions[market_name] = Position(market_name)

    def PlaceBuyOrder(self, market_name, bid_price, amount_in_base_currency):
        if self.base_balance >= amount_in_base_currency:
            self.base_balance -= amount_in_base_currency
            self.buy_orders[market_name] = [bid_price * BID_COEFFICIENT, amount_in_base_currency]

    def PlaceSellOrder(self, market_name, ask_price):
        if self.balances[market_name] > 0.0:
            self.sell_orders[market_name] = [ask_price * ASK_COEFFICIENT, self.balances[market_name]]
            self.balances[market_name] = 0.0

    def CancelBuyOrder(self, market_name):
        if 0 < len(self.buy_orders[market_name]):
            self.base_balance += self.buy_orders[market_name][1]
            self.buy_orders[market_name] = []

    def CancelSellOrder(self, market_name):
        if 0 < len(self.sell_orders[market_name]):
            self.balances[market_name] = self.sell_orders[market_name][1]
            self.sell_orders[market_name] = []

    def ExecuteBuyOrder(self, market_name, actual_price):
        if 0 < len(self.buy_orders[market_name]):
            if actual_price <= self.buy_orders[market_name][0]:
                """                                  base currency spent for this order                bid price"""
                self.balances[market_name] += self.buy_orders[market_name][1] * FEE_COEFFICIENT / self.buy_orders[market_name][0]
                self.buy_orders[market_name] = []

    def ExecuteSellOrder(self, market_name, actual_price):
        if 0 < len(self.sell_orders[market_name]):
            if actual_price >= self.sell_orders[market_name][0]:
                """                     number of coins to sell                             ask price"""
                self.base_balance += self.sell_orders[market_name][1] * FEE_COEFFICIENT * self.sell_orders[market_name][0]
                self.sell_orders[market_name] = []

    def Buy(self, market_name, rate, amount_in_base_currency):
        ret = False
        if self.base_balance > amount_in_base_currency:
            self.base_balance -= amount_in_base_currency
            self.balances[market_name] += amount_in_base_currency * FEE_COEFFICIENT / (rate * BID_COEFFICIENT)
            self.positions[market_name].entering_price = rate
            self.positions[market_name].in_position = True
            ret = True
        return ret

    def Sell(self, market_name, rate):
        ret = False
        if self.balances[market_name] > 0.0:
            self.base_balance += self.balances[market_name] * FEE_COEFFICIENT * rate * ASK_COEFFICIENT
            self.balances[market_name] = 0.0
            self.positions[market_name].in_position = False
            ret = True
        return ret

    def CalculateProfit(self, charts: Charts, sample):
        """Calculating profit in [%]"""
        _balance_all = self.base_balance
        for market_name in charts.close:
            if IsChartIndexInRange(sample, charts, market_name, offset=0):
                index = CalculateChartIndex(sample, charts, market_name)

                if self.balances[market_name] > 0.0 and charts.close[market_name][index] >= 0.0:
                    _balance_all += self.balances[market_name] * FEE_COEFFICIENT * \
                                    charts.close[market_name][index] * ASK_COEFFICIENT
        return 100 * (_balance_all - TEST_INITIAL_BALANCE) / TEST_INITIAL_BALANCE

    def Run(self, trigger_queue: TriggerQueue, charts: Charts, bankroll_management_by_algorithm=False):
        """
        This function simulates time and trading.
        Trading is done according to trigger queue which is previously calculated by an algorithm.
        """
        coins_bought = np.zeros(charts.max_len)
        coins_sold = np.zeros(charts.max_len)
        net_profit = np.full(charts.max_len, 0.0, float)

        for smpl in range(0, charts.max_len):
            buy_triggers = []
            sell_triggers = []
            buy_amounts_in_base_currency = dict()

            """Calculating the amounts of coins to buy in base currency"""
            if not bankroll_management_by_algorithm:
                for market_name in charts.close:
                    buy_amounts_in_base_currency[market_name] = self.base_balance * TEST_POSITION_SIZE_COEFFICIENT / TEST_NUM_OF_POSITIONS
                    if buy_amounts_in_base_currency[market_name] > TEST_MAX_POSITION_SIZE:
                        buy_amounts_in_base_currency[market_name] = TEST_MAX_POSITION_SIZE
                    elif buy_amounts_in_base_currency[market_name] < TEST_MIN_POSITION_SIZE:
                        buy_amounts_in_base_currency[market_name] = TEST_MIN_POSITION_SIZE
            else:
                for market_name in charts.close:
                    buy_amounts_in_base_currency[market_name] = 0.0

            """Filling up buy triggers (redundant buy triggers are possible, but it's not a problem)"""
            for trigger in trigger_queue.buy[smpl]:
                buy_triggers.append(trigger)

            """Filling up sell triggers (redundant sell triggers are possible, but it's not a problem)"""
            for trigger in trigger_queue.sell[smpl]:
                sell_triggers.append(trigger)

            """Placing buy orders"""
            for trigger in buy_triggers:
                index = CalculateChartIndex(smpl, charts, trigger.market_name)
                rate = charts.close[trigger.market_name][index]
                buy = self.Buy(trigger.market_name, rate, buy_amounts_in_base_currency[trigger.market_name])
                if buy:
                    coins_bought[smpl] += 1

            """Placing sell orders"""
            for trigger in sell_triggers:
                index = CalculateChartIndex(smpl, charts, trigger.market_name)
                rate = charts.close[trigger.market_name][index]
                sell = self.Sell(trigger.market_name, rate)
                if sell:
                    coins_sold[smpl] += 1

            net_profit[smpl] = self.CalculateProfit(charts, smpl)

        return {"net_profit": net_profit,
                "coins_bought": coins_bought,
                "coins_sold": coins_sold,
                "date": charts.date[charts.max_len_market]}
