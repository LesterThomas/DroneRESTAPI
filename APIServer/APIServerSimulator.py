"""This module provides the API endpoint for simulated drones to manage the simulator parameters"""

# This class handles the '/vehicle/(.*)/simulator' resource end-point which manages the Drone Simulator paramaters

import logging
import traceback
import json
import APIServerUtils
import requests
import web

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class Simulator:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        """This method handles the GET HTTP verb to get the simulator parameters. In this stateless server, it simply forwards the HTTP GET to the correct worker."""
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))
            my_logger.debug("vehicle_id = '" + vehicle_id + "'")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            result = requests.get(APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                                  "/vehicle/" + str(vehicle_id) + "/simulator?user_id=" + user)
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
        """This method handles the POST HTTP verb to change a simulator parameter. In this stateless server, it simply forwards the HTTP POST to the correct worker."""
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            dataStr = web.data()
            data_obj = json.loads(dataStr)
            data_obj['user_id'] = user

            my_logger.debug(
                "HTTP Proxy calling http post at %s with data %s",
                APIServerUtils.getWorkerURLforVehicle(vehicle_id) + "/vehicle/" + str(vehicle_id) + "/simulator",
                dataStr)

            result = requests.post(APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                                   "/vehicle/" + str(vehicle_id) + "/simulator", data=json.dumps(data_obj))

            my_logger.info("Return:%s", str(result))
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return result

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            # just here to suppor the CORS Cross-Origin security
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
