"""This module provides the API endpoint to manage the missions for a drone. A mission is a
series of actions that can be loaded to a drone and executed automatically"""

# Import DroneKit-Python
from dronekit import Command, mavutil

import web
import logging
import traceback
import json
import requests
import APIServerUtils

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class Mission:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        """This method handles the GET HTTP verb to get the mission. In this stateless server, it simply forwards the HTTP GET to the correct worker."""
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))
            my_logger.debug("vehicle_id = '" + vehicle_id + "'")
            user_id = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            result = requests.get(APIServerUtils.getWorkerURLforVehicle(user_id, vehicle_id) +
                                  "/vehicle/" + str(vehicle_id) + "/mission?user_id=" + user_id)
            my_logger.info("Return:%s", str(result))
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703

            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return result

    def POST(self, vehicle_id):
        """This method handles the POST HTTP verb to create a new mission. In this stateless server, it simply forwards the HTTP GET to the correct worker."""
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))
            user_id = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            dataStr = web.data()
            my_logger.info("dataStr: " + str(dataStr))

            data_obj = json.loads(dataStr)
            data_obj['user_id'] = user_id

            result = requests.post(APIServerUtils.getWorkerURLforVehicle(user_id, vehicle_id) +
                                   "/vehicle/" + str(vehicle_id) + "/mission", data=json.dumps(data_obj))

            my_logger.info("Return:%s", str(result.text))
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703

            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return result

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            APIServerUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703

            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output
