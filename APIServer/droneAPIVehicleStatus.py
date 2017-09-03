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
import droneAPIUtils


my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class vehicleStatus:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        try:
            my_logger.debug("GET: vehicle_id=" + str(vehicle_id))
            droneAPIUtils.applyHeadders()
            outputObj = {}

            actions = [{"method": "DELETE", "href": droneAPIUtils.homeDomain + "/vehicle/" +
                        str(vehicle_id), "title": "Delete connection to vehicle " + str(vehicle_id)}]

            json_str = droneAPIUtils.redisdB.get('connection_string:' + str(vehicle_id))
            individual_vehicle = json.loads(json_str)

            individual_vehicle['id'] = vehicle_id
            individual_vehicle['_links'] = {}
            individual_vehicle['_links']["self"] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id),
                "title": "Get status for vehicle " + str(vehicle_id) + "."}
            individual_vehicle['_links']['homeLocation'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/homeLocation",
                "title": "Get the home location for this vehicle"}
            individual_vehicle['_links']['command'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                "title": "Get the actions  for this vehicle."}
            individual_vehicle['_links']['mission'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/mission",
                "title": "Get the current mission commands from the vehicle."}
            individual_vehicle['_links']['simulator'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/simulator",
                "title": "Get the current simulator parameters from the vehicle."}
            individual_vehicle["_actions"] = actions
            output = json.dumps(individual_vehicle)
            my_logger.debug("Return: %s" % str(individual_vehicle))

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def DELETE(self, vehicle_id):
        """This method handles the DELETE HTTP verb to delete a vehicle. In this stateless server, it simply forwards the HTTP DELETE to the correct worker."""
        try:
            my_logger.info("DELETE: vehicle_id=" + str(vehicle_id))
            result = requests.delete(droneAPIUtils.getWorkerURLforVehicle(vehicle_id) + "/vehicle/" + str(vehicle_id))
            my_logger.debug("HTTP Proxy result status_code %s reason %s", result.status_code, result.reason)
            my_logger.debug("HTTP Proxy result text %s ", result.text)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return result.text

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            droneAPIUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output
