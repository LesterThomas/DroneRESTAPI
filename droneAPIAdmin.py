"""This module provides the API endpoint to administer the API service."""


import logging
import traceback
import json
import droneAPIUtils
import web

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class admin:

    def __init__(self):
        return

    def GET(self):
        try:
            my_logger.info("GET")
            droneAPIUtils.applyHeadders()
            outputObj = {}
            outputObj['_links'] = {"self": {"href": droneAPIUtils.homeDomain +
                                            "/admin", "title": "Administration functions for the Drone API service"}}

            availableActions = []
            availableActions.append({
                "name": "Rebuild dockerHostsArray",
                "title": "Rebuild the Array of available Docker Hosts and ports used.",
                "href": droneAPIUtils.homeDomain + "/admin",
                "method": "POST",
                "fields": [{"name": "name", "type": "string", "value": "Rebuild dockerHostsArray"}]
            })
            availableActions.append({
                "name": "Refresh containers",
                "title": "Restart all the docker containers (and create new ones if required).",
                "href": droneAPIUtils.homeDomain + "/admin",
                "method": "POST",
                "fields": [{"name": "name", "type": "string", "value": "Refresh containers"}]
            })
            outputObj['dockerHostsArray'] = droneAPIUtils.redisdB.get('dockerHostsArray')
            outputObj['Connections'] = []
            keys = droneAPIUtils.redisdB.keys("connectionString:*")
            for key in keys:
                jsonObjStr = droneAPIUtils.redisdB.get(key)
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
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def POST(self):
        try:
            my_logger.info("POST")
            droneAPIUtils.applyHeadders()
            data = json.loads(web.data())
            value = data["name"]
            outputObj = {}

            if (value == "Rebuild dockerHostsArray"):
                droneAPIUtils.rebuildDockerHostsArray()
                outputObj = {"status": "success"}

            if (value == "Refresh containers"):
                droneAPIUtils.validateAndRefreshContainers()
                outputObj = {"status": "success"}

            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def OPTIONS(self):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS")
            # just here to suppor the CORS Cross-Origin security
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
