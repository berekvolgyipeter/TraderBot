from DataManager import DataManager
from OnlineTesting.TestOrderManager import *
from Algorithms import Algorithms
from Configuration.Parameters import REFRESH_PERIODICITY
import datetime
import time


"""creating objects"""
data_manager = DataManager()
test_order_manager = TestOrderManager()
alg = Algorithms(datetime.datetime.now())

"""running infinite loop with a periodicity of REFRESH_PERIODICITY [seconds]"""
while True:
    trade_cycle_start_time = time.time()

    data = data_manager.Run()
    trigger_queue = alg.Run(data)
    test_order_manager.Run(trigger_queue, data)

    time.sleep(REFRESH_PERIODICITY - (time.time() - trade_cycle_start_time))

