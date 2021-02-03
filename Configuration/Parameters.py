"""This file contains some parameters for the algorithm"""


"""----------------------- constant parameters -----------------------"""
BASE_CURRENCY = "BTC"
BASE_CURRENCY_LEN = len(BASE_CURRENCY)
"""fee coefficient (every transaction has a 0.25% fee)"""
FEE_COEFFICIENT = 0.9975
"""Window sample numbers for indicators"""
ONE_DAY_WINDOW_5MIN = 288
ONE_WEEK_WINDOW_5MIN = 2016


"""----------------------- optimizable parameters -----------------------"""
"""Number of long positions (not actual long positions, but allowed number of coins to buy)"""
NUM_OF_POSITIONS = 8.0
"""Position size is multiplied by this number in order to avoid buying with insufficient funds"""
POSITION_SIZE_COEFFICIENT = 0.9975
"""Bids are multiplied by this relative amount"""
BID_COEFFICIENT = 1.0006
"""Asks are multiplied by this relative amount"""
ASK_COEFFICIENT = 0.9994
"""The program has a periodicity of this many seconds"""
REFRESH_PERIODICITY = 900
"""number of data samples stored in data buffers"""
NUM_OF_SAMPLES = 20


"""----------------------- safety parameters -----------------------"""
"""100K Satoshi"""
SATOSHI_100K = 0.001
if "USDT" == BASE_CURRENCY:
    coeff = 11000.0
else:
    coeff = 1.0
MAX_POSITION_SIZE = 0.3 * coeff
MIN_POSITION_SIZE = 2.5 * SATOSHI_100K * coeff
"""Buy orders are not cancelled if the filled quantity is below this BTC amount and 
sell orders are not cancelled if the remaining quantity is below this BTC amount"""
MIN_ORDER_SIZE = 1.5 * SATOSHI_100K * coeff
MIN_SELL_SIZE = SATOSHI_100K * coeff
"""Maximum time allowed for unfilled open orders in minutes (if the feature is used)"""
ORDER_TIMEOUT_MIN = 15
