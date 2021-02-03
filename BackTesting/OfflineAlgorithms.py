from BackTesting.TestUtilities import *


def Alg_HODL(charts: Charts):
    trigger_queue = TriggerQueue()

    for smpl in range(0, charts.max_len):
        trigger_queue.buy.append([])
        trigger_queue.sell.append([])

    for market_name in charts.close:
        if IsChartIndexInRange(1, charts, market_name, offset=0):
            trigger_queue.buy[0].append(Trigger(market_name, 0.0))

    return trigger_queue

