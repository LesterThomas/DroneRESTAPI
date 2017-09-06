"""This module provides the API endpoint for the collection of vehicles (drones). It also lets you create
a new simulated drone or a connection to a real drone."""

import web
import logging
import traceback
import json
import time
import math
import docker
import redis
import APIServerUtils
import requests

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class VehicleIndex:

    def __init__(self):
        return

    def GET(self):
        try:
            my_logger.debug("GET")
            APIServerUtils.applyHeadders()
            outputObj = []

            my_logger.info("Called by IP %s", web.ctx.ip)

            # get the query parameters
            query_parameters = web.input()
            my_logger.debug("Query parameters %s", str(query_parameters))
            keys = APIServerUtils.redisdB.keys("connection_string:*")
            for key in keys:
                my_logger.debug("key = '" + key + "'")
                json_str = APIServerUtils.redisdB.get(key)
                my_logger.debug("redisDbObj = '" + json_str + "'")
                individual_vehicle = json.loads(json_str)
                vehicle_id = key[18:]
                individual_vehicle["_links"] = {
                    "self": {
                        "href": APIServerUtils.homeDomain +
                        "/vehicle/" +
                        str(vehicle_id),
                        "title": "Get status for vehicle " +
                        str(vehicle_id)}}
                individual_vehicle["id"] = vehicle_id
                vehicle_started = ('vehicle_status' in individual_vehicle.keys())
                if vehicle_started:
                    if not(hasattr(query_parameters, 'status')):
                        # by default the Redis query will return extra details. delete unless status query parameter is passed
                        del individual_vehicle['vehicle_status']
                    outputObj.append(individual_vehicle)

            actions = '[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). For simulated vehicle you can also give the starting lat, lon, alt (of ground above sea level) and dir (initial direction the drone is pointing). The connection_string is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + \
                APIServerUtils.homeDomain + '/vehicle",\n"fields":[{"name":"vehicle_type", "type":{"listOfValues":["simulated","real"]}}, {"name":"connection_string","type":"string"}, {"name":"name","type":"string"}, {"name":"lat","type":"float"}, {"name":"lon","type":"float"}, {"name":"alt","type":"float"}, {"name":"dir","type":"float"}] }]\n'
            self = {"self": {"title": "Return the collection of available vehicles.", "href": APIServerUtils.homeDomain + "/vehicle"}}
            my_logger.debug("actions")
            my_logger.debug(actions)
            jsonResponse = '{"_embedded":{"vehicle":' + \
                json.dumps(outputObj) + '},"_actions":' + actions + ',"_links":' + json.dumps(self) + '}'
            my_logger.debug("Return: =" + jsonResponse)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})

        return jsonResponse

    def POST(self):
        """This method handles the POST HTTP verb to create a new vehicle. In this stateless server, it simply forwards the HTTP POST to the correct worker."""
        try:
            my_logger.info("POST:")
            APIServerUtils.applyHeadders()
            dataStr = web.data()
            result = requests.post(APIServerUtils.getNewWorkerURL() + "/vehicle", data=dataStr)
            my_logger.debug("HTTP Proxy result status_code %s reason %s", result.status_code, result.reason)
            my_logger.debug("HTTP Proxy result text %s ", result.text)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return result.text

    def OPTIONS(self):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: ")
            APIServerUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output
