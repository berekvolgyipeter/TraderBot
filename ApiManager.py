from datetime import datetime
import time
from Utilities import LogOutput

"""Right now these are the API methods and their keys which are used in the SW."""
"""IMPORTANT NOTE: this data structure has to be updated should a new method or key being used!"""
__check_criteria = {"getmarkets": ["BaseCurrency", "MarketName", "IsActive"],
                    "getticker": ["Bid", "Ask", "Last"],
                    "GetLatestTick": ["O", "H",  "L", "C", "T"],
                    "getmarketsummaries": ["MarketName", "Volume", "Last", "BaseVolume", "Bid", "Ask"],
                    "buylimit": ["uuid"],
                    "selllimit": ["uuid"],
                    # "cancel": [], it doesn't need to be checked since it has no keys
                    "getopenorders": ["OrderUuid", "OrderType", "Quantity", "QuantityRemaining"],
                    "getbalances": ["Currency", "Balance", "Available", "Pending"],
                    "getbalance": ["Currency", "Balance", "Available", "Pending"]}

__is_array = {"getmarkets": True,
              "getticker": False,
              "GetLatestTick": True,
              "getmarketsummaries": True,
              "buylimit": False,
              "selllimit": False,
              # "cancel": False,  # it hasn't been checked since it has no keys
              "getopenorders": True,
              "getbalances": True,
              "getbalance": False}


def CheckKeysAndTypes(method_ret_val):
    if (method_ret_val["method_name"] in __check_criteria) and method_ret_val["success"]:
        if __is_array[method_ret_val["method_name"]]:
            if method_ret_val["result"]:
                for key in __check_criteria[method_ret_val["method_name"]]:
                    for i in range(0, len(method_ret_val["result"])):
                        if (not method_ret_val["result"][i]) or (key not in method_ret_val["result"][i]):
                            method_ret_val["success"] = False
                            method_ret_val["message"] += "Missing key: " + key + "(array index: " + str(i) + "). "
                            method_ret_val["error_code"] = 'MISSING_KEY'
                        elif not method_ret_val["result"][i][key]:
                            if "getmarketsummaries" == method_ret_val["method_name"]:
                                # fill up with invalid value instead of None
                                method_ret_val["result"][i][key] = -1.0
                            elif ("getbalances" == method_ret_val["method_name"]) and ("Currency" != key):
                                method_ret_val["result"][i][key] = 0.0
                            elif ("getmarkets" == method_ret_val["method_name"]) and ("IsActive" == key):
                                method_ret_val["result"][i][key] = False
                            else:
                                method_ret_val["success"] = False
                                method_ret_val["message"] += " " + key + " returned with None(array index: " + str(i) + ")."
            else:
                if "getopenorders" == method_ret_val["method_name"]:
                    """Empty result field is a valid return value for these API methods."""
                    if method_ret_val["result"] is None:
                        method_ret_val["success"] = False
                        method_ret_val["message"] += " result field is None. "
                else:
                    method_ret_val["success"] = False
                    method_ret_val["message"] += " Empty result field. "

        else:
            for key in __check_criteria[method_ret_val["method_name"]]:
                if (not method_ret_val["result"]) or (key not in method_ret_val["result"]):
                    method_ret_val["success"] = False
                    method_ret_val["message"] += " Missing key: " + key + ". "
                    method_ret_val["error_code"] = 'MISSING_KEY'
                elif not method_ret_val["result"][key]:
                    if ("getbalance" == method_ret_val["method_name"]) and ("Currency" != key):
                        method_ret_val["result"][key] = 0.0
                    else:
                        method_ret_val["success"] = False
                        method_ret_val["message"] += key + " returned with None."
    return method_ret_val


def ExecuteApiCall(method):
    """Every API call is executed through this function"""
    ret = method
    ret = CheckKeysAndTypes(ret)
    """if the keys are missing from 'GetLatestTick' retrying won't solve the problem"""
    if not (("GetLatestTick" == ret["method_name"]) and ("MISSING_KEY" == ret["error_code"])):
        if not ret["success"]:
            LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + ": " +
                      "Failed API call: " + ret["method_name"] + ret["method_args"] +
                      ". Trying again. " +
                      ret["message"])
            time.sleep(2)
            ret = method
            ret = CheckKeysAndTypes(ret)
            if not ret["success"]:
                LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + ": " +
                          "Failed API call: " + ret["method_name"] + ret["method_args"] +
                          ". Trying again. " +
                          ret["message"])
                time.sleep(2)
                ret = method
                ret = CheckKeysAndTypes(ret)
                if not ret["success"]:
                    LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + ": " +
                              "Unable to execute API call: " + ret["method_name"] + ret["method_args"] + ". " +
                              ret["message"])
                else:
                    LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + ": " +
                              "Executing API call was now successful: " + ret["method_name"] + ret["method_args"] + ".")
            else:
                LogOutput(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]) + ": " +
                          "Executing API call was now successful: " + ret["method_name"] + ret["method_args"] + ".")

    return ret
