from DataManager import DataManager
from OrderManager import OrderManager
from Algorithms import Algorithms
from Logging import Logging
from Configuration.Parameters import REFRESH_PERIODICITY
import datetime
import time


"""creating objects"""
data_manager = DataManager()
order_manager = OrderManager()
alg = Algorithms(datetime.datetime.now())
log = Logging()

"""running infinite loop with a periodicity of REFRESH_PERIODICITY [seconds]"""
while True:
    trade_cycle_start_time = time.time()

    data = data_manager.Run()
    trigger_queue = alg.Run(data)
    order_manager.Run(trigger_queue)
    log.Run(data.last)

    time.sleep(REFRESH_PERIODICITY - (time.time() - trade_cycle_start_time))
