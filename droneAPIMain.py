"""The Main module of the drone API server. This module creates all the API URL endpoints and handles the index endpoint and contains the logic for catch-all (for any unhandled endpoints)."""
#!/usr/bin/env python

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from dronekit import Command, mavutil, APIException
# Import external modules
from collections import OrderedDict
import time
import json
import math
import warnings
import os
import web
import logging
import logging.handlers
import redis
import uuid
import boto3
import traceback
import docker

# Import  modules that are part of this app
import droneAPIUtils


class index:
    """THis class handles the root URL (sometimes called the EntryPoint) for the drone API."""

    def GET(self):
        """This method returns the root (sometimes called the EntryPoint) for the drone API.
        The returned string is a static set of links (to the other resource endpoints) and
        a simple description field for the API"""
        try:
            my_logger.info("GET")
            droneAPIUtils.applyHeadders()
            outputObj = {}
            outputObj['description'] = 'Welcome to the Drone API homepage. WARNING: This API is '
            'experimental - use at your own discression. The API allows you to interact with '
            'simulated or real drones through a simple hypermedia REST API. There is a HAL API '
            'Browser at http://droneapi.ddns.net:1235/static/hal-browser/browser.html and a test '
            ' client at http://droneapi.ddns.net:1235/static/app  The API is maintained at '
            'https://github.com/lesterthomas/DroneRESTAPI. This experimental API is part of '
            'the TM Forum Anything-as-a-Service Catalyst  '
            'https://projects.tmforum.org/wiki/display/PCT/A+Platform+for+IoT+and+Anything'
            '+as+a+Service+Catalyst'
            outputObj['_links'] = {
                'self': {
                    "href": droneAPIUtils.homeDomain,
                    "title": "Home-page (or EntryPoint) of the API"},
                'vehicle': {
                    "title": "Return the collection of available vehicles.",
                    "href": droneAPIUtils.homeDomain +
                    "/vehicle"}}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": e.message,
                               "args": e.args,
                               "traceback": traceLines})

        return output


class catchAll:
    """THis class handles any unknown URLs for the API. It provides Error and help information back to
    the client. It has methods for GET, POST and DELETE."""

    def GET(self, user):
        """THis method handles any unknown GET URL requests for the API."""
        try:
            my_logger.info("GET - catchAll")
            droneAPIUtils.applyHeadders()
            my_logger.debug(droneAPIUtils.homeDomain)
            outputObj = {
                "Error": "No API endpoint found. Try navigating to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicleId> for the status of vehicle #1 or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicleId>/action for the list of actions available for "
                         "vehicle <vehicleId>."}
            my_logger.info("Return: =" + json.dumps(outputObj))
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": e.message,
                               "args": e.args,
                               "traceback": traceLines})
        return json.dumps(outputObj)

    def POST(self, user):
        """THis method handles any unknown POST URL requests for the API."""
        try:
            my_logger.info("POST - catchAll")
            droneAPIUtils.applyHeadders()
            outputObj = {
                "Error": "No API endpoint found. Try navigating to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicleId> for the status of vehicle #1 or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicleId>/action for the list of actions available for "
                         "vehicle <vehicleId>."}
            my_logger.info("Return: =" + json.dumps(outputObj))
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": e.message,
                               "args": e.args,
                               "traceback": traceLines})
        return json.dumps(outputObj)

    def DELETE(self, user):
        """THis method handles any unknown DELETE URL requests for the API."""
        try:
            my_logger.info("DELETE - catchAll")
            droneAPIUtils.applyHeadders()
            outputObj = {
                "Error": "No API endpoint found. Try navigating to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle for list of vehicles or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicleId> for the status of vehicle #1 or to " +
                         droneAPIUtils.homeDomain +
                         "/vehicle/<vehicleId>/action for the list of actions available for "
                         "vehicle <vehicleId>."}
            my_logger.info("Return: =" + json.dumps(outputObj))
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": e.message,
                               "args": e.args,
                               "traceback": traceLines})
        return json.dumps(outputObj)


##########################################################################
# startup
##########################################################################


def startup():
    """This function starts the application. It initialises the logger, global data structures,
    Redis database and refreshes the drone docker containers. Finally it starts the web
    application that serves the API HTTP traffic."""

    print("Starting up at " + str(time.time()))

    droneAPIUtils.initaliseLogger()
    droneAPIUtils.initaliseGlobals()
    droneAPIUtils.initiliseRedisDB()
    droneAPIUtils.validateAndRefreshContainers()

    # set API url endpoints and class handlers. Each handler class is in its
    # own python module
    urls = (
        '/', 'index',
        '/vehicle/(.*)/action', 'droneAPIAction.action',
        '/vehicle/(.*)/homeLocation', 'droneAPIHomeLocation.homeLocation',
        '/vehicle/(.*)/mission', 'droneAPIMission.mission',
        '/vehicle/(.*)/authorizedZone', 'droneAPIAuthorizedZone.authorizedZone',
        '/vehicle/(.*)/simulator', 'droneAPISimulator.simulator',
        '/vehicle', 'droneAPIVehicleIndex.vehicleIndex',
        '/admin', 'droneAPIAdmin.admin',
        # was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
        '/vehicle/(.*)', 'droneAPIVehicleStatus.vehicleStatus',
        '/(.*)', 'catchAll'
    )

    # start API web application server
    app = web.application(urls, globals())
    app.run()
    return


if __name__ == "__main__":
    my_logger = logging.getLogger("DroneAPIServer." + str(__name__))
    startup()
