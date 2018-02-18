"""This module provides the API endpoint to administer the API service."""


import logging
import traceback
import json
import APIServerUtils
import requests
import web
import time
import math

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class Admin:

    def __init__(self):
        return

    def GET(self):
        try:
            my_logger.info("GET")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            outputObj = {}
            outputObj['_links'] = {"self": {"href": APIServerUtils.homeDomain +
                                            "/admin", "title": "Administration functions for the Drone API service"}}

            availableActions = []
            outputObj['_actions'] = availableActions

            workers = []
            keys = APIServerUtils.redisdB.keys("worker:*")
            for key in keys:
                worker = json.loads(APIServerUtils.redisdB.get(key))
                worker['id'] = key
                time_since_heartbeat = time.time() - worker['last_heartbeat']
                worker['time_since_heartbeat'] = round(time_since_heartbeat, 1)
                workers.append(worker)

            outputObj['workers'] = workers

            servers = []
            keys = APIServerUtils.redisdB.keys("server:*")
            for key in keys:
                server = json.loads(APIServerUtils.redisdB.get(key))
                server['id'] = key
                time_since_heartbeat = time.time() - server['last_heartbeat']
                server['time_since_heartbeat'] = round(time_since_heartbeat, 1)
                servers.append(server)
            outputObj['servers'] = servers

            outputObj['service_parameters'] = json.loads(APIServerUtils.redisdB.get('service_parameters'))

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

    def POST(self):
        try:
            my_logger.info("POST")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            dataStr = web.data()

            data = json.loads(dataStr)
            value = data["name"]
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

    def OPTIONS(self):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS")
            # just here to suppor the CORS Cross-Origin security
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
