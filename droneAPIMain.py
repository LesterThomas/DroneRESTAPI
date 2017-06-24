#!/usr/bin/env python

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException
# Import external modules
from collections import OrderedDict
import time, json, math, warnings, os, web, logging, logging.handlers, redis, uuid, boto3, traceback, docker

my_logger = logging.getLogger("DroneAPIServer."+str(__name__))




class index:        
    def GET(self):
        try:
            my_logger.info("GET")
            droneAPIUtils.applyHeadders()
            outputObj={}
            outputObj['description']='Welcome to the Drone API homepage. WARNING: This API is experimental - use at your own discression. The API allows you to interact with simulated or real drones through a simple hypermedia REST API. There is a HAL API Browser at http://droneapi.ddns.net:1235/static/hal-browser/browser.html and a test client at http://droneapi.ddns.net:1235/static/app  The API is maintained at https://github.com/lesterthomas/DroneRESTAPI. This experimental API is part of the TM Forum Anything-as-a-Service Catalyst  https://projects.tmforum.org/wiki/display/PCT/A+Platform+for+IoT+and+Anything+as+a+Service+Catalyst '
            outputObj['_links']={
                'self':{"href": droneAPIUtils.homeDomain, "title":"Home-page (or EntryPoint) of the API"},
                'vehicle': {
                        "title":"Return the collection of available vehicles.",
                        "href": droneAPIUtils.homeDomain+"/vehicle" }
                        }
            output=json.dumps(outputObj)
            my_logger.info( "Return: ="+output )
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             

        return output




class catchAll:
    def GET(self, user):
        try:
            my_logger.info( "GET - catchAll")
            droneAPIUtils.applyHeadders()
            my_logger.debug( droneAPIUtils.homeDomain)
            outputObj={"Error":"No API endpoint found. Try navigating to "+droneAPIUtils.homeDomain+"/vehicle for list of vehicles or to "+droneAPIUtils.homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+droneAPIUtils.homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
            my_logger.info( "Return: ="+json.dumps(outputObj) )
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)

    def POST(self, user):
        try:
            my_logger.info( "POST - catchAll")
            droneAPIUtils.applyHeadders()
            outputObj={"Error":"No API endpoint found. Try navigating to "+droneAPIUtils.homeDomain+"/vehicle for list of vehicles or to "+droneAPIUtils.homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+droneAPIUtils.homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
            my_logger.info( "Return: ="+json.dumps(outputObj) )
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)


##################################################################################################
#startup
##################################################################################################


# Import  modules that are part of this app
import droneAPIUtils




#set API url endpoints and class handlers. Each handler class is in its own python module
urls = (
    '/', 'index',
    '/vehicle/(.*)/action', 'droneAPIAction.action',
    '/vehicle/(.*)/homeLocation', 'droneAPIHomeLocation.homeLocation',
    '/vehicle/(.*)/mission', 'droneAPIMission.mission',
    '/vehicle/(.*)/authorizedZone', 'droneAPIAuthorizedZone.authorizedZone',
    '/vehicle/(.*)/simulator', 'droneAPISimulator.simulator',
    '/vehicle', 'droneAPIVehicleIndex.vehicleIndex',
    '/vehicle/(.*)', 'droneAPIVehicleStatus.vehicleStatus', #was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
    '/(.*)', 'catchAll'
)

#start API web application server
app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()





