import datetime
import csv
import numpy as np
from Bittrex import Bittrex
from Utilities import Data
from Configuration.Keys import *
from Configuration.Parameters import *
from Configuration.DirectoryLocations import *
from ApiManager import ExecuteApiCall


class DataManager:
    """
    This class collects, saves and manages data
    """
    def __init__(self):
        """-1 is used as invalid value everywhere"""
        self.__api = Bittrex(API_KEY, API_SECRET)
        self.__data = Data()
        self.__last_valid_data = Data()
        self.__market_sum = dict()
        self.__market_sum_last_valid = dict()
        self.__validity_vector = dict()
        self.__market_sum_validity_vector = np.full(NUM_OF_SAMPLES, -1, int)

    def CollectData(self):
        """
        This function collects market data by API.
        """

        """init self.__market_sum_last_valid"""
        try:
            if self.__market_sum["success"]:
                pass
        except KeyError:
            self.__market_sum_last_valid = {"success": False, "result": [], "message": None}

        """Get the new data"""
        self.__market_sum = ExecuteApiCall(self.__api.get_market_summaries())

        """Update last valid values"""
        if self.__market_sum["success"]:
            self.__market_sum_last_valid = self.__market_sum

    def RefreshDataBuffers(self):
        """
        shifts every element of price_charts for each market one index below
        and the last element of the buffer is refreshed
        """

        self.__market_sum_validity_vector = np.roll(self.__market_sum_validity_vector, -1)
        if self.__market_sum["success"]:
            self.__market_sum_validity_vector[-1] = 0
        else:
            self.__market_sum_validity_vector[-1] = -1

        for result in self.__market_sum_last_valid["result"]:
            """Only the BASE_CURRENCY base markets are used"""
            if BASE_CURRENCY == result["MarketName"][:BASE_CURRENCY_LEN]:
                market_name = result["MarketName"]

                """Initializing data and last valid data values"""
                if market_name in self.__data.last:
                    """Left shifting"""
                    self.__data.last[market_name] =        np.roll(self.__data.last[market_name], -1)
                    self.__data.bid[market_name] =         np.roll(self.__data.bid[market_name], -1)
                    self.__data.ask[market_name] =         np.roll(self.__data.ask[market_name], -1)
                    self.__data.volume[market_name] =      np.roll(self.__data.volume[market_name], -1)
                    self.__data.base_volume[market_name] = np.roll(self.__data.base_volume[market_name], -1)
                    self.__validity_vector[market_name] =  np.roll(self.__validity_vector[market_name], -1)
                else:
                    self.__data.last[market_name] =        np.full(NUM_OF_SAMPLES, -1.0, float)
                    self.__data.bid[market_name] =         np.full(NUM_OF_SAMPLES, -1.0, float)
                    self.__data.ask[market_name] =         np.full(NUM_OF_SAMPLES, -1.0, float)
                    self.__data.volume[market_name] =      np.full(NUM_OF_SAMPLES, -1.0, float)
                    self.__data.base_volume[market_name] = np.full(NUM_OF_SAMPLES, -1.0, float)
                    self.__validity_vector[market_name] =  np.full(NUM_OF_SAMPLES, -1, int)

                if market_name not in self.__last_valid_data.last:
                    self.__last_valid_data.last[market_name] = -1.0
                    self.__last_valid_data.bid[market_name] = -1.0
                    self.__last_valid_data.ask[market_name] = -1.0
                    self.__last_valid_data.volume[market_name] = -1.0
                    self.__last_valid_data.base_volume[market_name] = -1.0

                """Update last valid data values"""
                if result["Last"] and (result["Last"] > 0.0):
                    self.__last_valid_data.last[market_name] = result["Last"]
                    self.__validity_vector[market_name][-1] = 0
                else:
                    self.__validity_vector[market_name][-1] = -1
                if result["Bid"] and result["Bid"] > 0.0:
                    self.__last_valid_data.bid[market_name] = result["Bid"]
                if result["Ask"] and result["Ask"] > 0.0:
                    self.__last_valid_data.ask[market_name] = result["Ask"]
                if result["Volume"] and result["Volume"] > 0.0:
                    self.__last_valid_data.volume[market_name] = result["Volume"]
                if result["BaseVolume"] and result["BaseVolume"] > 0.0:
                    self.__last_valid_data.base_volume[market_name] = result["BaseVolume"]

                """Update last elements of data buffers"""
                self.__data.last[market_name][-1] =        self.__last_valid_data.last[market_name]
                self.__data.bid[market_name][-1] =         self.__last_valid_data.bid[market_name]
                self.__data.ask[market_name][-1] =         self.__last_valid_data.ask[market_name]
                self.__data.volume[market_name][-1] =      self.__last_valid_data.volume[market_name]
                self.__data.base_volume[market_name][-1] = self.__last_valid_data.base_volume[market_name]

    def CheckValidity(self):
        """
        sets the validity flag of each market
        """
        half_len = int(NUM_OF_SAMPLES / 2)
        fail_tolerance_vv = -3
        fail_tolerance_vv_fresh_samples = -2
        fail_tolerance_msvv = -4
        fail_tolerance_msvv_fresh_samples = -2

        """
        a market is considered valid if it has at least (NUM_OF_SAMPLES - fail_tolerance_vv) number of valid samples and
        maximum fail_tolerance_vv_fresh_samples invalid samples in last half of the array
        the same principle is true for market summaries"""
        for market_name in self.__data.last:
            self.__data.validity[market_name] = True
            if np.sum(self.__validity_vector[market_name]) < fail_tolerance_vv:
                self.__data.validity[market_name] = False
            if np.sum(self.__validity_vector[market_name][-half_len:]) < fail_tolerance_vv_fresh_samples:
                self.__data.validity[market_name] = False
            for price in self.__data.last[market_name]:
                if price < 0.0:
                    self.__data.validity[market_name] = False
                    break

        if np.sum(self.__market_sum_validity_vector) < fail_tolerance_msvv or\
           np.sum(self.__market_sum_validity_vector[-half_len:]) < fail_tolerance_msvv_fresh_samples:
            for market_name in self.__data.last:
                self.__data.validity[market_name] = False

    def SaveDataToFile(self):
        """
        This function saves data to files.
        If the data is invalid it writes the previous values to the files again.
        """

        date = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4])

        for market_name in self.__last_valid_data.last:
            file_path = CHARTS_LOCATION_BITTREX + str(market_name) + ".csv"
            with open(file_path, 'a', newline='') as csvfile:
                logfilewriter = csv.writer(csvfile)
                logfilewriter.writerow([date, " " +
                                        str(self.__last_valid_data.last[market_name]),
                                        str(self.__last_valid_data.bid[market_name]),
                                        str(self.__last_valid_data.ask[market_name]),
                                        str(self.__last_valid_data.volume[market_name]),
                                        str(self.__last_valid_data.base_volume[market_name])])
                csvfile.close()

    def Run(self):
        """This is the main function, it is called periodically."""
        self.CollectData()
        self.RefreshDataBuffers()
        self.CheckValidity()
        self.SaveDataToFile()

        return self.__data
