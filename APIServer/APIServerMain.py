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
import APIServerUtils


class Index(object):  # pylint: disable=R0903
    """THis class handles the root URL (sometimes called the EntryPoint) for the drone API."""

    def __init__(self):
        return

    def GET(self):  # pylint: disable=R0201
        """This method returns the root (sometimes called the EntryPoint) for the drone API.
        The returned string is a static set of links (to the other resource endpoints) and
        a simple description field for the API"""
        try:
            my_logger.info("GET")

            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            output_obj = {}
            output_obj['description'] = """Welcome to the Drone API homepage. WARNING: This API is
            experimental - use at your own discression. The API allows you to interact with
            simulated or real drones through a simple hypermedia REST API. There is a HAL API
            Browser at http://droneapi.ddns.net:1235/static/hal-browser/browser.html and a test
             client at http://droneapi.ddns.net:1235/static/app  The API is maintained at
            https://github.com/lesterthomas/DroneRESTAPI. This experimental API is part of
            the TM Forum Anything-as-a-Service Catalyst
            https://projects.tmforum.org/wiki/display/PCT/A+Platform+for+IoT+and+Anything
            +as+a+Service+Catalyst"""
            output_obj['_links'] = {
                'self': {
                    "href": APIServerUtils.homeDomain,
                    "title": "Home-page (or EntryPoint) of the API"},
                'vehicle': {
                    "title": "Return the collection of available vehicles.",
                    "href": APIServerUtils.homeDomain +
                    "/vehicle"}}
            output = json.dumps(output_obj)
            my_logger.info("Return: =" + output)
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})

        return output


class CatchAll(object):
    """THis class handles any unknown URLs for the API. It provides Error and help information back
    to the client. It has methods for GET, POST and DELETE."""

    def GET(self, url):  # pylint: disable=R0201
        """THis method handles any unknown GET URL requests for the API."""
        try:
            my_logger.info("GET - CatchAll")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            my_logger.debug(APIServerUtils.homeDomain)
            output_obj = {
                "Error": "No API endpoint found. Try navigating to " +
                         APIServerUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         APIServerUtils.homeDomain +
                         "/vehicle/<vehicle_id> for the status of vehicle #1 or to " +
                         APIServerUtils.homeDomain +
                         "/vehicle/<vehicle_id>/action for the list of actions available for "
                         "vehicle <vehicle_id>."}
            my_logger.info("Return: =" + json.dumps(output_obj))
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})
        return json.dumps(output_obj)

    def POST(self, url):  # pylint: disable=R0201
        """THis method handles any unknown POST URL requests for the API."""
        try:
            my_logger.info("POST - CatchAll")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            output_obj = {
                "Error": "No API endpoint found. Try navigating to " +
                         APIServerUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         APIServerUtils.homeDomain +
                         "/vehicle/<vehicle_id> for the status of vehicle #1 or to " +
                         APIServerUtils.homeDomain +
                         "/vehicle/<vehicle_id>/action for the list of actions available for "
                         "vehicle <vehicle_id>."}
            my_logger.info("Return: =" + json.dumps(output_obj))
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})
        return json.dumps(output_obj)

    def DELETE(self, url):  # pylint: disable=R0201
        """THis method handles any unknown DELETE URL requests for the API."""
        try:
            my_logger.info("DELETE - CatchAll")
            user = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()
            output_obj = {
                "Error": "No API endpoint found. Try navigating to " +
                         APIServerUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         APIServerUtils.homeDomain +
                         "/vehicle/<vehicle_id> for the status of vehicle #1 or to " +
                         APIServerUtils.homeDomain +
                         "/vehicle/<vehicle_id>/action for the list of actions available for "
                         "vehicle <vehicle_id>."}
            my_logger.info("Return: =" + json.dumps(output_obj))
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
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

    print "Starting up at " + str(time.time())

    APIServerUtils.initaliseLogger()
    APIServerUtils.initaliseGlobals()
    APIServerUtils.initiliseRedisDB()

    # set API url endpoints and class handlers. Each handler class is in its
    # own python module
    urls = (
        '/', 'Index',
        '/vehicle/(.*)/command', 'APIServerCommand.Command',
        '/vehicle/(.*)/homeLocation', 'APIServerHomeLocation.HomeLocation',
        '/vehicle/(.*)/mission', 'APIServerMission.Mission',
        '/vehicle/(.*)/authorizedZone', 'APIServerAuthorizedZone.AuthorizedZone',
        '/vehicle/(.*)/simulator', 'APIServerSimulator.Simulator',
        '/vehicle', 'APIServerVehicleIndex.VehicleIndex',
        '/admin', 'APIServerAdmin.Admin',
        '/user', 'APIServerUser.User',
        # was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
        '/vehicle/(.*)', 'APIServerVehicleStatus.VehicleStatus',
        '/(.*)', 'CatchAll'
    )

    # start API web application server
    app = web.application(urls, globals())
    app.run()
    return


if __name__ == "__main__":
    my_logger = logging.getLogger("DroneAPIServer." + str(__name__))  # pylint: disable=C0103
    startup()
