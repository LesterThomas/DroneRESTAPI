"""Thi module manages the API endpoint for an individual vehicle (drone). It returns
the status for a drone and allows you to delete a drone"""

import web
import logging
import traceback
import json
import time
import math
import docker
import requests
import APIServerUtils


my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class VehicleStatus:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        try:
            APIServerUtils.applyHeadders()
            user_id = APIServerUtils.getUserAuthorization()
            my_logger.info("GET: vehicle_id: %s, user_id %s", str(vehicle_id), user_id)

            outputObj = {}

            actions = [{"method": "DELETE", "href": APIServerUtils.homeDomain + "/vehicle/" +
                        str(vehicle_id), "title": "Delete connection to vehicle " + str(vehicle_id)}]

            json_str = APIServerUtils.redisdB.get("vehicle:" + user_id + ":" + str(vehicle_id))
            individual_vehicle = json.loads(json_str)

            individual_vehicle['id'] = vehicle_id
            individual_vehicle['_links'] = {}
            individual_vehicle['_links']["self"] = {
                "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id),
                "title": "Get status for vehicle " + str(vehicle_id) + "."}
            individual_vehicle['_links']['homeLocation'] = {
                "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/homeLocation",
                "title": "Get the home location for this vehicle"}
            individual_vehicle['_links']['command'] = {
                "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                "title": "Get the actions  for this vehicle."}
            individual_vehicle['_links']['mission'] = {
                "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/mission",
                "title": "Get the current mission commands from the vehicle."}
            individual_vehicle['_links']['simulator'] = {
                "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/simulator",
                "title": "Get the current simulator parameters from the vehicle."}
            individual_vehicle["_actions"] = actions
            output = json.dumps(individual_vehicle)
            my_logger.debug("Return: %s" % str(individual_vehicle))

        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output

    def DELETE(self, vehicle_id):
        """This method handles the DELETE HTTP verb to delete a vehicle. In this stateless server, it simply forwards the HTTP DELETE to the correct worker."""
        try:
            my_logger.info("DELETE: vehicle_id=" + str(vehicle_id))
            user_id = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            result = requests.delete(APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                                     "/vehicle/" + str(vehicle_id) + "?user_id=" + user_id)
            my_logger.debug("HTTP Proxy result status_code %s reason %s", result.status_code, result.reason)
            my_logger.debug("HTTP Proxy result text %s ", result.text)

        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return result.text

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
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
