"""This module provides the API endpoint to administer the API service."""


import logging
import traceback
import json
import APIServerUtils
import requests
import web

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
            availableActions.append({
                "name": "Rebuild dockerHostsArray",
                "title": "Rebuild the Array of available Docker Hosts and ports used.",
                "href": APIServerUtils.homeDomain + "/admin",
                "method": "POST",
                "fields": [{"name": "name", "type": "string", "value": "Rebuild dockerHostsArray"}]
            })
            availableActions.append({
                "name": "Refresh containers",
                "title": "Restart all the docker containers (and create new ones if required).",
                "href": APIServerUtils.homeDomain + "/admin",
                "method": "POST",
                "fields": [{"name": "name", "type": "string", "value": "Refresh containers"}]
            })
            outputObj['dockerHostsArray'] = APIServerUtils.redisdB.get('dockerHostsArray')
            outputObj['Connections'] = []
            keys = APIServerUtils.redisdB.keys("connectionString:*")
            for key in keys:
                jsonObjStr = APIServerUtils.redisdB.get(key)
                jsonObj = json.loads(jsonObjStr)
                connectionString = jsonObj['connectionString']
                dockerContainerId = jsonObj['dockerContainerId']

                vehicleName = jsonObj['name']
                vehicleType = jsonObj['vehicleType']
                dockerContainerId = jsonObj['dockerContainerId']
                droneId = key[17:]
                hostIp = connectionString[4:-6]
                port = connectionString[-5:]
                outputObj['Connections'].append({"connectionString": connectionString,
                                                 "dockerContainerId": dockerContainerId,
                                                 "vehicleName": vehicleName,
                                                 "vehicleType": vehicleType,
                                                 "droneId": droneId,
                                                 "hostIp": hostIp,
                                                 "port": port})

            outputObj['_actions'] = availableActions
            outputObj['_actions'] = availableActions

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

            if (value == "Rebuild dockerHostsArray"):
                APIServerUtils.rebuildDockerHostsArray()
                outputObj = {"status": "success"}

            if (value == "Refresh containers"):
                # delegate this call to all the worker containers

                workerURLs = APIServerUtils.getAllWorkerURLs()
                for workerURL in workerURLs:
                    result = requests.post(workerURL + "/admin", data=dataStr)
                    my_logger.info("Return from worker %s:%s", str(workerURL), str(result.text))

                outputObj = {"status": "success"}

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
