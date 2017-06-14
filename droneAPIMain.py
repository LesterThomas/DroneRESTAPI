#!/usr/bin/env python

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException
# Import external modules
from collections import OrderedDict
import time, json, math, warnings, os, web, logging, logging.handlers, redis, uuid, time, boto3, traceback, docker

my_logger = logging.getLogger('MyLogger')

# Import  modules that are part of this app
import droneAPISimulator, droneAPIUtils, droneAPIAction, droneAPIMission

def validateRedisData(redisdB):
    #test the redis dB
    #remove any old entries (and any old docker containers)
    dockerHostsArray=[]
    redisdB.set('foo', 'bar')
    value = redisdB.get('foo')
    if (value=='bar'):
        my_logger.info("Connected to Redis dB")
    else:
        my_logger.error("Can not connect to Redis dB")
        raise Exception('Can not connect to Redis dB on port 6379')

    #print out the relavant redisdB data
    droneObjKeys=redisdB.keys("connectionString:*")
    for key in droneObjKeys:
        jsonObjStr=redisdB.get(key)
        my_logger.info( "removing key = '"+key+"'" + ",redisDbObj = '"+jsonObjStr+"'")
        redisdB.delete(key)

    dockerHostsArray=json.loads(redisdB.get("dockerHostsArray"))

    #check that I can access Docker on each host and to delete any existing containers
    index=-1
    for dockerHost in dockerHostsArray:
        index=index+1
        canAccessHost=True
        try :
            my_logger.info( "dockerHost = '"+dockerHost['internalIP']+"'")
            dockerClient = docker.DockerClient(version='1.27',base_url='unix://var/run/docker.sock')
            #dockerClient = docker.from_env()
            for container in dockerClient.containers.list():
                imageName=str(container.image)
                my_logger.info(container.id + " "+ container.name + " '" + imageName +"'")
                if (imageName=="<Image: 'lesterthomas/dronesim:1.7'>"):
                    my_logger.warn("stopping container "+container.id )
                    container.stop()
                    dockerClient.containers.prune(filters=None)

        except Exception as e: 
            my_logger.warn( "Can not connect to host: "+dockerHost['internalIP'])
            canAccessHost=False
            dockerHostsArray.pop(index)

    dockerHostsArray=[{"internalIP":"localhost","usedPorts":[]}]
    dockerHostsArrayString=json.dumps(dockerHostsArray)
    redisdB.set("dockerHostsArray",dockerHostsArrayString)

    my_logger.info("dockerHostsArray")
    my_logger.info(dockerHostsArray)

    redisdB.set("dockerHostsArray",json.dumps(dockerHostsArray))


    return




class index:        
    def GET(self):
        try:
            my_logger.info( "#### Method GET of index #####")
            droneAPIUtils.applyHeadders()
            outputObj={}
            outputObj['description']='Welcome to the Drone API homepage. WARNING: This API is experimental - use at your own discression. The API allows you to interact with simulated or real drones through a simple hypermedia REST API. There is a HAL API Browser at http://droneapi.ddns.net:1235/static/hal-browser/browser.html and a test client at http://droneapi.ddns.net:1235/static/app  The API is maintained at https://github.com/lesterthomas/DroneRESTAPI. This experimental API is part of the TM Forum Anything-as-a-Service Catalyst  https://projects.tmforum.org/wiki/display/PCT/A+Platform+for+IoT+and+Anything+as+a+Service+Catalyst '
            outputObj['_links']={
                'self':{"href": homeDomain, "title":"Home-page (or EntryPoint) of the API"},
                'vehicle': {
                        "title":"Return the collection of available vehicles.",
                        "href": homeDomain+"/vehicle" }
                        }
            output=json.dumps(outputObj)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             

        return output




class catchAll:
    def GET(self, user):
        try:
            my_logger.info( "#### Method GET of catchAll ####")
            droneAPIUtils.applyHeadders()
            my_logger.debug( homeDomain)
            outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)

    def POST(self, user):
        try:
            my_logger.info( "#### Method POST of catchAll ####")
            droneAPIUtils.applyHeadders()
            outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)


#Set logging framework
LOG_FILENAME = 'droneapi.log'
my_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
my_logger.addHandler(handler)
my_logger.propegate=False

my_logger.info("##################################################################################")
my_logger.info("Starting DroneAPI server")
my_logger.info("##################################################################################")

try:
    defaultHomeDomain=os.environ['DRONE_URL']
except Exception as e: 
    my_logger.error("Can't get environment variable DRONE_URL")
    my_logger.exception(e)
    tracebackStr = traceback.format_exc()
    traceLines = tracebackStr.split("\n")   

connectionDict={} #holds a dictionary of DroneKit connection objects
connectionNameTypeDict={} #holds the additonal name, type and starttime for the conections
actionArrayDict={} #holds recent actions executied by each drone
authorizedZoneDict={} #holds zone authorizations for each drone
redisdB = redis.Redis(host='redis', port=6379) #redis or localhost
validateRedisData(redisdB)





urls = (
    '/', 'index',
    '/vehicle/(.*)/action', 'droneAPIAction.action',
    '/vehicle/(.*)/homeLocation', 'droneAPIHomeLocation.homeLocation',
    '/vehicle/(.*)/mission', 'droneAPIMission.mission',
    '/vehicle/(.*)/authorizedZone', 'authorizedZone',
    '/vehicle/(.*)/simulator', 'droneAPISimulator.simulator',
    '/vehicle', 'droneAPIVehicleIndex.vehicleIndex',
    '/vehicle/(.*)', 'droneAPIVehicleStatus.vehicleStatus', #was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
    '/(.*)', 'catchAll'
)

homeDomain = os.getenv('HOME_DOMAIN', defaultHomeDomain)
my_logger.debug( "Home Domain:"  + homeDomain)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()





