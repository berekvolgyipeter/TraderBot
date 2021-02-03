import socket
from Configuration.DirectoryLocations import SERVER_IP_ADDRESS
from datetime import datetime
from Logging import LogOutput


def CheckServerIsAlive():
    """Returns True if the server is alive and False otherwise."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((SERVER_IP_ADDRESS, 22))
        ret = True
    except socket.error as e:
        LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + "Server is not alive: %s" % e)
        ret = False
    s.close()
    return ret
