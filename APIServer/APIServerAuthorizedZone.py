"""This module provides the API endpoint to manage the zones a drone is authorised to fly in. The
existing authorized zones are returned as part of the vehicleStatus. This module allows you
to request a new authorised zone."""


import web
import logging
import traceback
import json
import APIServerUtils


my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class AuthorizedZone:

    def __init__(self):
        return

    def POST(self, vehicle_id):
        """This method handles the POST requests to create a new Authorized Zone. In this stateless server, it simply forwards the HTTP POST to the correct worker."""
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))
            my_logger.debug("vehicle_id = '" + vehicle_id + "'")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            data_obj = json.loads(dataStr)
            data_obj['user_id'] = user

            result = requests.post(APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                                   "/vehicle/" + str(vehicle_id) + "/command", data=json.dumps(data_obj))
            my_logger.debug("HTTP Proxy result status_code %s reason %s", result.status_code, result.reason)
            my_logger.debug("HTTP Proxy result text %s ", result.text)

            my_logger.info("Return: %s", result.text)
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return result.text

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
