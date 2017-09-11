"""This module provides the API endpoint to retrieve the home location for a drone. The home
location is the position the drone took off from."""


import logging
import traceback
import json
import requests
import APIServerUtils

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class HomeLocation:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        """This method handles the GET HTTP verb to get the homeLocation. In this stateless server, it simply forwards the HTTP GET to the correct worker."""
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            result = requests.get(APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                                  "/vehicle/" + str(vehicle_id) + "/homeLocation?user_id=" + user)
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

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: ")
            APIServerUtils.applyHeadders()
            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output
