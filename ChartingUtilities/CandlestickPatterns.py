"""Bullish reversal candlestick patterns"""
"""They occur after a decline in price"""
"""
If the market is trending higher, then wait for a pullback towards Support
If the price makes a pullback towards Support, then wait for a bullish reversal candlestick pattern
If there’s a bullish reversal candlestick pattern, then make sure the size of it is larger than the earlier candles (signalling strong rejection)
"""

def Hammer(_open, _high, _low, _close):
    """
    Little to no upper shadow
    The price closes at the top ¼ of the range
    The lower shadow is about 2 or 3 times the length of the body
    """
    ret = False
    if _close >= _open:
        body_top = _close
        body_bottom = _open
    else:
        body_top = _open
        body_bottom = _close
    candle_range = _high - _low
    body = body_top - body_bottom

    if(((_high - body_top) <= (0.1 * candle_range)) and
       ((_high - _close) <= (0.25 * candle_range)) and
       ((2.0 * body) <= (body_bottom - _low)) and
       (body > (0.0025 * _close))):
        ret = True

    return ret


def BullishEngulfing(open1, high1, low1, close1,
                     open2, high2, low2, close2):
    """
    The first candle has a bearish close
    The second candle closes bullish
    The body of the second candle completely “covers” the body of the first candle (without taking into consideration the shadow)
    """
    ret = False

    if((open1 > close1) and
       (open2 < close2) and
       (close2 > open1)):
        ret = True

    return ret


def Piercing(open1, high1, low1, close1,
             open2, high2, low2, close2):
    """
    The first candle has a bearish close
    The second candle closes bullish
    The body of the second candle closes beyond the halfway mark of the first candle
    """
    ret = False

    if((open1 > close1) and
       (open2 < close2) and
       (open1 >= close2 > (low1 + 0.5 * (high1 - low1)))):
        ret = True

    return ret


def TweezerBottom(open1, high1, low1, close1,
                  open2, high2, low2, close2):
    """
    The first candle shows rejection of lower prices
    The second candle re-tests the low of the previous candle and closes higher
    """
    ret = False
    candle1_range = high1 - low1
    upper_shadow1 = high1 - open1
    lower_shadow1 = close1 - low1
    body1 = open1 - close1
    upper_shadow2 = high2 - close2
    lower_shadow2 = open2 - low2

    if((open1 > close1) and  # First candle bearish
       (open2 < close2) and  # Second candle bullish
       (lower_shadow1 >= 0.5 * body1) and (upper_shadow1 < 0.6 * body1) and
       (lower_shadow2 >= 0.5 * body1) and (upper_shadow2 < body1) and
       ((low1 - 0.12 * candle1_range) <= low2 <= (low1 + 0.12 * candle1_range))):
        ret = True

    return ret


def MorningStar(open1, high1, low1, close1,
                open2, high2, low2, close2,
                open3, high3, low3, close3):
    """
    The first candle has a bearish close
    The second candle has a small range, but the length of the lower wick doesn't matter
    The third candle closes aggressively higher (more than 50% of the first candle)
    """
    ret = False
    body1 = open1 - close1

    if((open1 > close1) and
       ((high2 - max(open2, close2)) < (0.4 * body1)) and
       (abs(open2 - close2) < (0.2 * body1)) and
       (close3 > (close1 + 0.5 * body1))):
        ret = True

    return ret


def MorningStar2(open1, high1, low1, close1,
                 open2, high2, low2, close2,
                 open3, high3, low3, close3,
                 open4, high4, low4, close4):
    """
    The first candle has a bearish close
    The middle candles have small ranges, but the lengths of the lower wicks don't matter
    The third candle closes aggressively higher (more than 50% of the first candle)
    """
    ret = False
    body1 = open1 - close1
    middle_body_bottom = min(open2, close2, open3, close3)
    middle_range_without_lower_wicks = max(high2, high3) - middle_body_bottom
    middle_body = max(open2, close2, open3, close3) - middle_body_bottom

    if((open1 > close1) and
       (middle_range_without_lower_wicks < (0.4 * body1)) and
       (middle_body < (0.2 * body1)) and
       (close4 > (close1 + 0.5 * body1))):
        ret = True

    return ret


def MorningStar3(open1, high1, low1, close1,
                 open2, high2, low2, close2,
                 open3, high3, low3, close3,
                 open4, high4, low4, close4,
                 open5, high5, low5, close5):
    """
    The first candle has a bearish close
    The middle candles have small ranges, but the lengths of the lower wicks don't matter
    The third candle closes aggressively higher (more than 50% of the first candle)
    """
    ret = False
    body1 = open1 - close1
    middle_body_bottom = min(open2, close2, open3, close3, open4, close4)
    middle_range_without_lower_wicks = max(high2, high3, high4) - middle_body_bottom
    middle_body = max(open2, close2, open3, close3, open4, close4) - middle_body_bottom

    if((open1 > close1) and
       (middle_range_without_lower_wicks < (0.5 * body1)) and
       (middle_body < (0.5 * body1)) and
       (close5 > (close1 + 0.5 * body1))):
        ret = True

    return ret


"""Bearish reversal candlestick patterns"""
"""They occur after an increase in price"""
"""
If the market is trending lower, then wait for a pullback towards Resistance
If the price pullback towards Resistance, then wait for a bearish reversal candlestick pattern
If there’s a bearish reversal candlestick pattern, then make sure the size of it is larger than the earlier candles (signalling strong rejection)
If there’s a strong price rejection, then go short on next candle’s open
And vice versa for long setups
"""

def ShootingStar(_open, _high, _low, _close):
    """
    Little to no lower shadow
    The price closes at the bottom ¼ of the range
    The upper shadow is about 2 or 3 times the length of the body
    """
    ret = False
    if _close >= _open:
        body_top = _close
        body_bottom = _open
    else:
        body_top = _open
        body_bottom = _close
    candle_range = _high - _low
    body = body_top - body_bottom

    if(((body_bottom - _low) <= (0.1 * candle_range)) and
       ((_close - _low) <= (0.25 * candle_range)) and
       ((2.0 * body) <= (_high - body_top)) and
       (body > (0.0025 * _close))):
        ret = True

    return ret


def BearishEngulfing(open1, high1, low1, close1,
                     open2, high2, low2, close2):
    """
    The first candle has a bullish close
    The second candle closes bearish
    The body of the second candle completely “covers” the body first candle (without taking into consideration the shadow)
    """
    ret = False

    if((open1 < close1) and
       (open2 > close2) and
       (close2 < open1)):
        ret = True

    return ret


def DarkCloudCover(open1, high1, low1, close1,
                   open2, high2, low2, close2):
    """
    The first candle has a bullish close
    The second candle closes bearish
    The body of the second candle closes beyond the halfway mark of the first candle
    """
    ret = False

    if((open1 < close1) and
       (open2 > close2) and
       (open1 <= close2 < (low1 + 0.5 * (high1 - low1)))):
        ret = True

    return ret


def TweezerTop(open1, high1, low1, close1,
               open2, high2, low2, close2):
    """
    The first candle shows rejection of higher prices
    The second candle re-tests the high of the previous candle and closes lower
    """
    ret = False
    candle1_range = high1 - low1
    upper_shadow1 = high1 - close1
    lower_shadow1 = open1 - low1
    body1 = close1 - open1
    upper_shadow2 = high2 - open2
    lower_shadow2 = close2 - low2

    if((open1 < close1) and  # First candle bullish
       (open2 > close2) and  # Second candle bearish
       (upper_shadow1 >= 0.5 * body1) and (lower_shadow1 < 0.6 * body1) and
       (upper_shadow2 >= 0.5 * body1) and (lower_shadow2 < body1) and
       ((high1 - 0.12 * candle1_range) <= high2 <= (high1 + 0.12 * candle1_range))):
        ret = True

    return ret


def EveningStar(open1, high1, low1, close1,
                open2, high2, low2, close2,
                open3, high3, low3, close3):
    """
    The first candle has a bullish close
    The second candle has a small range, but the length of the upper wick doesn't matter
    The third candle closes aggressively lower (more than 50% of the first candle)
    """
    ret = False
    body1 = close1 - open1
    body2 = abs(open2 - close2)

    if((open1 < close1) and
       ((max(open2, close2) - low2) < (0.4 * body1)) and
       (body2 < (0.2 * body1)) and
       (close3 < (close1 - 0.5 * body1))):
        ret = True

    return ret


def EveningStar2(open1, high1, low1, close1,
                 open2, high2, low2, close2,
                 open3, high3, low3, close3,
                 open4, high4, low4, close4):
    """
    The first candle has a bullish close
    The middle candles have small ranges, but the lengths of the upper wicks don't matter
    The last candle closes aggressively lower (more than 50% of the first candle)
    """
    ret = False
    body1 = close1 - open1
    middle_body_top = max(open2, close2, open3, close3)
    middle_range_without_upper_wicks = middle_body_top - min(low2, low3)
    middle_body = middle_body_top - min(open2, close2, open3, close3)

    if((open1 < close1) and
       (middle_range_without_upper_wicks < (0.4 * body1)) and
       (middle_body < (0.2 * body1)) and
       (close4 < (close1 - 0.5 * body1))):
        ret = True

    return ret


def EveningStar3(open1, high1, low1, close1,
                 open2, high2, low2, close2,
                 open3, high3, low3, close3,
                 open4, high4, low4, close4,
                 open5, high5, low5, close5):
    """
    The first candle has a bullish close
    The middle candles have small ranges, but the lengths of the upper wicks don't matter
    The last candle closes aggressively lower (more than 50% of the first candle)
    """
    ret = False
    body1 = close1 - open1
    middle_body_top = max(open2, close2, open3, close3, open4, close4)
    middle_range_without_upper_wicks = middle_body_top - min(low2, low3, low4)
    middle_body = middle_body_top - min(open2, close2, open3, close3, open4, close4)

    if((open1 < close1) and
       (middle_range_without_upper_wicks < (0.4 * body1)) and
       (middle_body < (0.25 * body1)) and
       (close5 < (close1 - 0.5 * body1))):
        ret = True

    return ret


"""Continuation candlestick patterns"""
def RisingThreeMethod():  #TODO: finish
    """
    The first candle is a large bullish candle
    The second, third and fourth candle has a smaller range and body
    The fifth candle is a large-bodied candle that closes above the highs of the first candle
    """
    pass

def FallingThreeMethod():  #TODO: finish
    """
    The first candle is a large bearish candle
    The second, third and fourth candle has a smaller range and body
    The fifth candle is a large-bodied candle that closes below the lows of the first candle
    """
    pass

def BullishHarami(open1, high1, low1, close1,
                  open2, high2, low2, close2):
    """
    The first candle is bullish and larger than the second candle
    The second candle has a small body and range (it can be bullish or bearish)
    """
    ret = False
    candle1_body = close1 - open1
    candle2_range = high2 - low2

    if((close1 > open1) and
       (candle1_body > 2.0 * candle2_range)):
        ret = True

    return ret

def BearishHarami(open1, high1, low1, close1,
                  open2, high2, low2, close2):
    """
    The first candle is bearish and larger than the second candle
    The second candle has a small body and range (it can be bullish or bearish)
    """
    ret = False
    candle1_body = open1 - close1
    candle2_range = high2 - low2

    if((close1 < open1) and
       (candle1_body > 2.0 * candle2_range)):
        ret = True

    return ret
