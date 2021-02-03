from Configuration.Parameters import SATOSHI_100K

"""initial balance in the selected base currency"""
TEST_INITIAL_BALANCE = 1.0
"""Number of positions"""
TEST_NUM_OF_POSITIONS = 8.0
"""Position size is multiplied by this number in order to avoid buying with insufficient funds"""
TEST_POSITION_SIZE_COEFFICIENT = 0.9975
"""Position size saturation"""
TEST_MAX_POSITION_SIZE = 1.0
TEST_MIN_POSITION_SIZE = 2.5 * SATOSHI_100K


POLONIEX_USDT_MARKETS = [
    'USDT_ATOM',
    'USDT_BAT',
    'USDT_BCHABC',
    'USDT_BCHSV',
    'USDT_BTC',
    'USDT_DASH',
    'USDT_DGB',
    'USDT_DOGE',
    'USDT_EOS',
    'USDT_ETC',
    'USDT_ETH',
    'USDT_GNT',
    'USDT_GRIN',
    'USDT_LSK',
    'USDT_LTC',
    'USDT_MANA',
    'USDT_NXT',
    'USDT_QTUM',
    'USDT_REP',
    'USDT_SC',
    'USDT_STR',
    'USDT_XMR',
    'USDT_XRP',
    'USDT_ZEC',
    'USDT_ZRX',
]

POLONIEX_BTC_MARKETS = [
    'BTC_AMP',
    'BTC_ARDR',
    'BTC_BCH',
    'BTC_BCN',
    'BTC_BTCD',
    'BTC_BTM',
    'BTC_BTS',
    'BTC_BURST',
    'BTC_CLAM',
    'BTC_DASH',
    'BTC_DCR',
    'BTC_DGB',
    'BTC_EMC2',
    'BTC_ETC',
    'BTC_ETH',
    'BTC_EXP',
    'BTC_FCT',
    'BTC_GAME',
    'BTC_GNO',
    'BTC_GNT',
    'BTC_GRC',
    'BTC_HUC',
    'BTC_LBC',
    'BTC_LSK',
    'BTC_LTC',
    'BTC_MAID',
    'BTC_NAV',
    'BTC_NEOS',
    'BTC_NMC',
    'BTC_NXT',
    'BTC_OMNI',
    'BTC_PASC',
    'BTC_POT',
    'BTC_PPC',
    'BTC_REP',
    'BTC_SBD',
    'BTC_SC',
    'BTC_STEEM',
    'BTC_STR',
    'BTC_STRAT',
    'BTC_SYS',
    'BTC_VIA',
    'BTC_VRC',
    'BTC_VTC',
    'BTC_XBC',
    'BTC_XCP',
    'BTC_XEM',
    'BTC_XMR',
    'BTC_XPM',
    'BTC_XRP',
    'BTC_ZEC',
    'BTC_ZRX'
]
