"""The Main module of the drone API server. This module creates all the API URL endpoints and
handles the index endpoint and contains the logic for catch-all (for any unhandled endpoints)."""
#!/usr/bin/env python

# Import external modules
import time
import json
import logging
import logging.handlers
import traceback
import web

# Import  modules that are part of this app
import droneAPIUtils


class CatchAll(object):
    """THis class handles any unknown URLs for the API. It provides Error and help information back
    to the client. It has methods for GET, POST and DELETE."""

    def GET(self):  # pylint: disable=R0201
        """THis method handles any unknown GET URL requests for the API."""
        try:
            my_logger.info("GET - CatchAll")
            droneAPIUtils.applyHeadders()
            my_logger.debug(droneAPIUtils.homeDomain)
            output_obj = {
                "Error": "No API endpoint found. Try navigating to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicle_id> for the status of vehicle #1 or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicle_id>/action for the list of actions available for "
                         "vehicle <vehicle_id>."}
            my_logger.info("Return: =" + json.dumps(output_obj))
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})
        return json.dumps(output_obj)

    def POST(self):  # pylint: disable=R0201
        """THis method handles any unknown POST URL requests for the API."""
        try:
            my_logger.info("POST - CatchAll")
            droneAPIUtils.applyHeadders()
            output_obj = {
                "Error": "No API endpoint found. Try navigating to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicle_id> for the status of vehicle #1 or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicle_id>/action for the list of actions available for "
                         "vehicle <vehicle_id>."}
            my_logger.info("Return: =" + json.dumps(output_obj))
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})
        return json.dumps(output_obj)

    def DELETE(self):  # pylint: disable=R0201
        """THis method handles any unknown DELETE URL requests for the API."""
        try:
            my_logger.info("DELETE - CatchAll")
            droneAPIUtils.applyHeadders()
            output_obj = {
                "Error": "No API endpoint found. Try navigating to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicle_id> for the status of vehicle #1 or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicle_id>/action for the list of actions available for "
                         "vehicle <vehicle_id>."}
            my_logger.info("Return: =" + json.dumps(output_obj))
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})
        return json.dumps(output_obj)


##########################################################################
# startup
##########################################################################


def startup():
    """This function starts the application. It initialises the logger, global data structures,
    Redis database and refreshes the drone docker containers. Finally it starts the web
    application that serves the API HTTP traffic."""

    droneAPIUtils.initaliseLogger()
    droneAPIUtils.initaliseGlobals()
    droneAPIUtils.initiliseRedisDB()
    droneAPIUtils.validateAndRefreshContainers()
    droneAPIUtils.startBackgroundWorker()

    # set API url endpoints and class handlers. Each handler class is in its
    # own python module
    urls = (
        '/vehicle/(.*)/command', 'droneAPICommand.Command',
        '/vehicle/(.*)/homeLocation', 'droneAPIHomeLocation.homeLocation',
        '/vehicle/(.*)/mission', 'droneAPIMission.mission',
        '/vehicle/(.*)/authorizedZone', 'droneAPIAuthorizedZone.authorizedZone',
        '/vehicle/(.*)/simulator', 'droneAPISimulator.simulator',
        '/vehicle', 'droneAPIVehicleIndex.vehicleIndex',
        '/admin', 'droneAPIAdmin.admin',
        # was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
        '/vehicle/(.*)', 'droneAPIVehicleStatus.vehicleStatus',
        '/(.*)', 'CatchAll'
    )

    # start API web application server
    droneAPIUtils.webApp = web.application(urls, globals())
    droneAPIUtils.webApp.run()

    return


if __name__ == "__main__":
    my_logger = logging.getLogger("DroneAPIServer." + str(__name__))  # pylint: disable=C0103
    startup()
