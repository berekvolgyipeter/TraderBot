from uuid import getnode as get_mac


CRYPTOCURRENCY_LOCATION_BEREK_HP = "C:/Users/HP/Documents/CryptoCurrency/"
CRYPTOCURRENCY_LOCATION_VPS = "/root/"

mac = get_mac()
# if 0000000000000 == mac:
if mac:
    CRYPTOCURRENCY_LOCATION = CRYPTOCURRENCY_LOCATION_BEREK_HP
else:
    CRYPTOCURRENCY_LOCATION = CRYPTOCURRENCY_LOCATION_VPS

PROJECT_LOCATION = CRYPTOCURRENCY_LOCATION + "Projects/TraderBot_old/"
CHARTS_LOCATION = CRYPTOCURRENCY_LOCATION + "Charts/"
CHARTS_LOCATION_POLONIEX = CHARTS_LOCATION + "poloniex/"
CHARTS_LOCATION_BITTREX = CHARTS_LOCATION + "bittrex/"

SERVER_IP_ADDRESS = ""