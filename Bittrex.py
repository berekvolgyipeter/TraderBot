import time
import hmac
import hashlib
import requests
import json
from urllib.parse import urlencode

try:
    from Crypto.Cipher import AES
    import getpass
    import ast
    encrypted = True
except ImportError:
    encrypted = False


BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

BASE_URL = 'https://bittrex.com/api/v1.1/%s/'
MARKET_SET = {'buylimit', 'selllimit', 'cancel', 'getopenorders', 'sellmarket', 'buymarket'}
ACCOUNT_SET = {'getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory'}

"""for API 2.0"""
BASE_URL_2_0 = "https://bittrex.com/Api/v2.0/"
MARKETS_SET_2_0_PUB = {'GetMarkets', 'GetMarketSummaries'}
MARKET_SET_2_0_PUB = {'GetMarketSummary', 'GetTicks', 'GetLatestTick', 'GetMarketHistory'}
MARKET_SET_2_0_AUTH = {'TradeBuy', 'TradeSell', 'TradeCancel'}
ORDERS_SET_2_0_AUTH = {'GetOrderHistory'}
CURRENCIES_SET_2_0_PUB = {'GetBTCPrice'}


def encrypt(api_key, api_secret, export=True, export_fn='secrets.json'):
    cipher = AES.new(getpass.getpass('Input encryption password (string will not show)'))
    api_key_n = cipher.encrypt(api_key)
    api_secret_n = cipher.encrypt(api_secret)
    api = {'key': str(api_key_n), 'secret': str(api_secret_n)}
    if export:
        with open(export_fn, 'w') as outfile:
            json.dump(api, outfile)
    return api


def using_requests(request_url, apisign):
    try:
        return requests.get(
            request_url,
            headers={"apisign": apisign}
        ).json()
    except Exception as ex:
        template = "\n\t\t\t\t\t\tAn exception of type {0} occurred. Arguments:\n\t\t\t\t\t\t{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return {"success": False,
                "message": message,
                "result": None}


def using_requests_post(request_url, apisign):
    try:
        return requests.post(
            request_url,
            headers={"apisign": apisign}
        ).json()
    except Exception as ex:
        template = "\n\t\t\t\t\t\tAn exception of type {0} occurred. Arguments:\n\t\t\t\t\t\t{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return {"success": False,
                "message": message,
                "result": None}


class Bittrex:
    """
    Used for requesting Bittrex with API key and API secret
    """

    def __init__(self, api_key, api_secret, dispatch=using_requests):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.dispatch = dispatch

    def decrypt(self):
        if encrypted:
            cipher = AES.new(getpass.getpass('Input decryption password (string will not show)'))
            try:
                self.api_key = ast.literal_eval(self.api_key) if type(self.api_key) == str else self.api_key
                self.api_secret = ast.literal_eval(self.api_secret) if type(self.api_secret) == str else self.api_secret
            except:
                pass
            self.api_key = cipher.decrypt(self.api_key).decode()
            self.api_secret = cipher.decrypt(self.api_secret).decode()
        else:
            raise ImportError('"pycrypto" module has to be installed')

    def api_query(self, method, options=None):
        """
        Queries Bittrex with given method and options
        :param method: Query method for getting info
        :type method: str
        :param options: Extra options for query
        :type options: dict
        :return: JSON response from Bittrex
        :rtype : dict
        """
        if not options:
            options = dict()
        nonce = str(int(time.time() * 1000))
        method_set = 'public'

        if method in MARKET_SET:
            method_set = 'market'
        elif method in ACCOUNT_SET:
            method_set = 'account'

        request_url = (BASE_URL % method_set) + method + '?'

        if method_set != 'public':
            request_url += 'apikey=' + self.api_key + "&nonce=" + nonce + '&'

        request_url += urlencode(options)

        apisign = hmac.new(self.api_secret.encode(),
                           request_url.encode(),
                           hashlib.sha512).hexdigest()
        ret = self.dispatch(request_url, apisign)
        ret['method_name'] = method
        ret['method_args'] = str(options)
        ret['error_code'] = ''

        return ret

    def api_query_2_0(self, method, options=None):
        """
        Queries Bittrex with given method and options for the 2.0 API
        :param method: Query method for getting info
        :type method: str
        :param options: Extra options for query
        :type options: dict
        :return: JSON response from Bittrex
        :rtype : dict
        """
        if not options:
            options = dict()

        if method in MARKETS_SET_2_0_PUB:
            method_set = 'pub/markets/'
        elif method in MARKET_SET_2_0_PUB:
            method_set = 'pub/market/'
        elif method in MARKET_SET_2_0_AUTH:
            method_set = 'auth/market/'
        elif method in ORDERS_SET_2_0_AUTH:
            method_set = 'auth/orders/'
        elif method in CURRENCIES_SET_2_0_PUB:
            method_set = 'pub/currencies/'
        else:
            method_set = ''

        request_url = BASE_URL_2_0 + method_set + method + '?'

        if method_set[0:3] != 'pub':
            nonce = str(int(time.time() * 1000))
            request_url += 'apikey=' + self.api_key + "&nonce=" + nonce + '&'
            self.dispatch = using_requests_post

        request_url += urlencode(options)

        apisign = hmac.new(self.api_secret.encode(),
                           request_url.encode(),
                           hashlib.sha512).hexdigest()
        ret = self.dispatch(request_url, apisign)
        ret['method_name'] = method
        ret['method_args'] = str(options)
        ret['error_code'] = ''

        return ret

    """------------------- Public API -------------------"""
    def get_markets(self):
        """
        Used to get the open and available trading markets
        at Bittrex along with other meta data.
        :return: Available market info in JSON
        :rtype : dict
        """
        return self.api_query('getmarkets')

    def get_currencies(self):
        """
        Used to get all supported currencies at Bittrex
        along with other meta data.
        :return: Supported currencies info in JSON
        :rtype : dict
        """
        return self.api_query('getcurrencies')

    def get_ticker(self, market):
        """
        Used to get the current tick values for a market.
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :return: Current values for given market in JSON
        :rtype : dict
        """
        return self.api_query('getticker', {'market': market})

    def get_market_summaries(self):
        """
        Used to get the last 24 hour summary of all active exchanges
        :return: Summaries of active exchanges in JSON
        :rtype : dict
        """
        return self.api_query('getmarketsummaries')

    def get_market_summary(self, market):
        """
        Used to get the last 24 hour summary of all active exchanges in specific coin

        :param market: String literal for the market(ex: BTC-XRP)
        :type market: str

        :return: Summaries of active exchanges of a coin in JSON
        :rtype : dict
        """
        return self.api_query('getmarketsummary', {'market': market})

    def get_orderbook(self, market, depth_type="both", depth=20):
        """
        Used to get retrieve the orderbook for a given market
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param depth_type: buy, sell or both to identify the type of orderbook to return.
            Use constants buy, sell, both
        :type depth_type: str
        :param depth: how deep of an order book to retrieve. Max is 100, default is 20
        :type depth: int
        :return: Orderbook of market in JSON
        :rtype : dict
        """
        return self.api_query('getorderbook', {'market': market, 'type': depth_type, 'depth': depth})

    def get_market_history(self, market, count=20):
        """
        Used to retrieve the latest trades that have occurred for a
        specific market.
        /market/getmarkethistory
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param count: Number between 1-100 for the number of entries to return (default = 20)
        :type count: int
        :return: Market history in JSON
        :rtype : dict
        """
        return self.api_query('getmarkethistory', {'market': market, 'count': count})

    """------------------- Market API -------------------"""
    def buy_limit(self, market, quantity, rate):
        """
        Used to place a buy order in a specific market. Use buylimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work
        /market/buylimit
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param quantity: The amount to purchase
        :type quantity: float
        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float
        :return:
        :rtype : dict
        """
        return self.api_query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_limit(self, market, quantity, rate):
        """
        Used to place a sell order in a specific market. Use selllimit to place
        limit orders Make sure you have the proper permissions set on your
        API keys for this call to work
        /market/selllimit
        :param market: String literal for the market (ex: BTC-LTC)
        :type market: str
        :param quantity: The amount to purchase
        :type quantity: float
        :param rate: The rate at which to place the order.
            This is not needed for market orders
        :type rate: float
        :return:
        :rtype : dict
        """
        return self.api_query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def cancel(self, uuid):
        """
        Used to cancel a buy or sell order
        /market/cancel
        :param uuid: uuid of buy or sell order
        :type uuid: str
        :return:
        :rtype : dict
        """
        return self.api_query('cancel', {'uuid': uuid})

    def get_open_orders(self, market=None):
        """
        Get all orders that you currently have opened. A specific market can be requested
        /market/getopenorders
        :param market: String literal for the market (ie. BTC-LTC)
        :type market: str
        :return: Open orders info in JSON
        :rtype : dict
        """
        if market is None:
            return self.api_query('getopenorders')
        else:
            return self.api_query('getopenorders', {'market': market})

    """------------------- Account API -------------------"""
    def get_balances(self):
        """
        Used to retrieve all balances from your account
        /account/getbalances
        :return: Balances info in JSON
        :rtype : dict
        """
        return self.api_query('getbalances', {})

    def get_balance(self, currency):
        """
        Used to retrieve the balance from your account for a specific currency
        /account/getbalance
        :param currency: String literal for the currency (ex: LTC)
        :type currency: str
        :return: Balance info in JSON
        :rtype : dict
        """
        return self.api_query('getbalance', {'currency': currency})

    def get_deposit_address(self, currency):
        """
        Used to generate or retrieve an address for a specific currency
        /account/getdepositaddress
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :return: Address info in JSON
        :rtype : dict
        """
        return self.api_query('getdepositaddress', {'currency': currency})

    def withdraw(self, currency, quantity, address):
        """
        Used to withdraw funds from your account
        /account/withdraw
        :param currency: String literal for the currency (ie. BTC)
        :type currency: str
        :param quantity: The quantity of coins to withdraw
        :type quantity: float
        :param address: The address where to send the funds.
        :type address: str
        :return:
        :rtype : dict
        """
        return self.api_query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})

    def get_order(self, uuid):
        """
        Used to get details of buy or sell order
        /account/getorder

        :param uuid: uuid of buy or sell order
        :type uuid: str

        :return:
        :rtype : dict
        """
        return self.api_query('getorder', {'uuid': uuid})

    def get_order_history(self, market=None):
        """
        Used to reterieve order trade history of account
        /account/getorderhistory
        :param market: optional a string literal for the market (ie. BTC-LTC). If ommited, will return for all markets
        :type market: str
        :return: order history in JSON
        :rtype : dict
        """
        if not market:
            return self.api_query('getorderhistory')
        else:
            return self.api_query('getorderhistory', {'market': market})

    """--------------------------------------------------------------------------------------------"""
    """------------------------------------API version 2.0-----------------------------------------"""
    """--------------------------------------------------------------------------------------------"""

    def get_ticks(self, market, tick_interval="fiveMin", _=None):
        """
        Gets the candles for a market.
        Probably _ is a timestamp. tickInterval must be in [“oneMin”, “fiveMin”, “thirtyMin”, “hour”, “day”].
        example:
        https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=BTC-CVC&tickInterval=thirtyMin&_=1500915289433
        :param: marketName:string, tickInterval:string, _:int
        :return:
                {
                    success : true,
                    message : "",
                    result : [ // Array of candle objects.
                    {
                        BV: 13.14752793,          // base volume
                        C: 0.000121,              // close
                        H: 0.00182154,            // high
                        L: 0.0001009,             // low
                        O: 0.00182154,            // open
                        T: "2017-07-16T23:00:00", // timestamp
                        V: 68949.3719684          // 24h volume
                    },
                    ...
                    { ... }]
                }
        """
        return self.api_query_2_0('GetTicks', {'marketName': market, 'tickInterval': tick_interval, '_': _})

    def get_latest_tick(self, market, tick_interval="fiveMin", _=None):
        """
        Gets the last candle for a market.
        Probably _ is a timestamp. tickInterval must be in [“oneMin”, “fiveMin”, “thirtyMin”, “hour”, “day”].
        example:
        https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=BTC-CVC&tickInterval=thirtyMin&_=1500915289433
        :param: marketName:string, tickInterval:string, _:int
        :return:
                {
                    success : true,
                    message : "",
                    result : [ // Array of candle objects.
                    {
                        BV: 13.14752793,          // base volume
                        C: 0.000121,              // close
                        H: 0.00182154,            // high
                        L: 0.0001009,             // low
                        O: 0.00182154,            // open
                        T: "2017-07-16T23:00:00", // timestamp
                        V: 68949.3719684          // 24h volume
                    },
                    ...
                    { ... }]
                }
        """
        return self.api_query_2_0('GetLatestTick', {'marketName': market, 'tickInterval': tick_interval, '_': _})

    def trade_buy(self, market, order_type, quantity, rate,
                  time_in_effect="GOOD_TIL_CANCELED",
                  condition_type="NONE",
                  target=0,
                  request_verification_token="HIDDEN_FOR_PRIVACY"):
        """
        Creates a buy order.
        example:
             https://bittrex.com/api/v2.0/auth/market/TradeBuy with data
             { MarketName: "BTC-DGB, OrderType:"LIMIT",
             Quantity: 10000.02, Rate: 0.0000004,
             TimeInEffect:"GOOD_TIL_CANCELED",
             ConditionType: "NONE", Target: 0,
              __RequestVerificationToken: "HIDDEN_FOR_PRIVACY"}
        :param:
            MarketName:string, OrderType:string, Quantity:float, Rate:float,
            TimeInEffect:string,ConditionType:string, Target:int __RequestVerificationToken:string
        :return:
        {
            success : true,
            message : "",
            result : { //results are different from example, this is a real response from a real request.
                BuyOrSell: "Buy",
                MarketCurrency: "DGB",
                MarketName: "BTC-DGB",
                OrderId: "cb31d615-91eb-408f-87c3-b35b7d751817",
                OrderType: "LIMIT",
                Quantity: 49875,
                Rate:1e-8
            }
        }
        """
        return self.api_query_2_0('TradeBuy', {'MarketName': market, 'OrderType': order_type,
                                               'Quantity': quantity, 'Rate': rate,
                                               'TimeInEffect': time_in_effect, 'ConditionType': condition_type,
                                               'Target': target,
                                               '__RequestVerificationToken': request_verification_token})

    def get_order_history2(self):
        return self.api_query_2_0('GetOrderHistory')
