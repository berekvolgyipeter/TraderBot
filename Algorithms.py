from Indicators import *
from Utilities import *
import numpy as np


class Algorithms:
    def __init__(self, start_date):
        self.__ema = dict()
        self.__start_date = start_date
        self.__markets_to_trade = []

    @staticmethod
    def SellInvalidCoins(validity):
        sell_triggers = []
        for market_name in validity:
            if not validity[market_name]:
                sell_triggers.append(market_name)
        return sell_triggers

    def Alg_e2(self, charts: Data, buy_hysteresis=-0.015, sell_hysteresis=0.015, ema_period=15):
        """algorithm 2: low pass filter + hysteresis comparator"""
        triggers = TriggerQueue()

        """Update the markets to trade once a day"""
        if DailyTrigger(self.__start_date):
            self.__markets_to_trade = GetTopVolumeCoins(charts, number_of_coins=30)

        for market_name in charts.last:
            if charts.validity[market_name]:
                if market_name not in self.__ema:
                    self.__ema[market_name] = FirFilterExp(charts.last[market_name][-1],
                                                           np.average(charts.last[market_name][-ema_period:]),
                                                           ema_period)
                else:
                    self.__ema[market_name] = FirFilterExp(charts.last[market_name][-1],
                                                           self.__ema[market_name],
                                                           ema_period)

                """Calculating relative price difference to filtered last sample"""
                price_diff = charts.last[market_name][-1] - self.__ema[market_name]
                price_diff /= self.__ema[market_name]

                if price_diff <= buy_hysteresis and market_name in self.__markets_to_trade:
                    triggers.buy.append(market_name)
                elif price_diff >= sell_hysteresis:
                    triggers.sell.append(market_name)

            elif market_name in self.__ema:
                del(self.__ema[market_name])

        return triggers

    def Run(self, charts: Data):
        triggers = self.Alg_e2(charts)
        sell_triggers_from_invalidity = self.SellInvalidCoins(charts.validity)
        for market_name in sell_triggers_from_invalidity:
            triggers.sell.append(market_name)
            triggers.invalidity_sell.append(market_name)
        return triggers
