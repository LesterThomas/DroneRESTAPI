"""This module provides the API endpoint to administer the API service."""

import sys
import logging
import traceback
import json
import droneAPIUtils
import web


class admin:

    def __init__(self):
        self.logger = logging.getLogger("DroneAPIWorker." + str(__name__))
        self.logger.info("droneAPIRedis Initialised admin")
        return

    def GET(self):
        try:
            self.logger.info("GET")
            droneAPIUtils.applyHeadders()
            outputObj = {}
            outputObj['_links'] = {"self": {"href": droneAPIUtils.homeDomain +
                                            "/admin", "title": "Administration functions for the Drone API service"}}

            availableActions = []

            #get this workers stats
            outputObj['worker_record']=droneAPIUtils.getWorkerDetails()
            self.logger.info("worker_record: = %s", outputObj['worker_record'])

            if (outputObj['worker_record']['running']==False):
                self.logger.info("Get Admin raising 500 error")
                raise web.HTTPError(500)

            outputObj['_actions'] = availableActions
            output = json.dumps(outputObj)
            self.logger.info("Return: =" + output)
        except Exception as e:
            self.logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def POST(self):
        try:
            self.logger.info("POST")
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
            self.logger.info("Return: =" + output)
        except Exception as e:
            self.logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def OPTIONS(self):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            self.logger.info("OPTIONS")
            # just here to suppor the CORS Cross-Origin security
            droneAPIUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            self.logger.info("Return: =" + output)
        except Exception as e:
            self.logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output
