#!/usr/bin/env python

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException
from collections import OrderedDict
import time, json, math, warnings
import os
import web
import logging
import logging.handlers
import redis
import uuid
import time
import boto3
import traceback

config={"maxSimulatedDrones":20, "maxDistance":1000, "groundSpeed":10,"droneSimImage":"ami-5be0f43f", "droneSimSecurityGroup":"sg-fd0c8394"}



#Set logging framework
LOG_FILENAME = 'droneapi.log'
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
my_logger.addHandler(handler)
my_logger.propegate=False

my_logger.info("##################################################################################")
my_logger.info("Starting DroneAPI server")
my_logger.info("##################################################################################")

versionDev=False #prod
defaultHomeDomain='' 
redisdB = None
if (versionDev):
    redisdB = redis.Redis(host='localhost', port=6379) #redis or localhost
    defaultHomeDomain='http://localhost:1235' #droneapi.ddns.net
    my_logger.info("Dev version connected to Redis at " + str(redisdB) + " and home domain of " + str(defaultHomeDomain))
else:
    my_logger.info("Prod version connected to Redis at " + str(redisdB) + " and home domain of " + str(defaultHomeDomain))
    defaultHomeDomain='http://droneapi.ddns.net:1235' 
    redisdB = redis.Redis(host='redis', port=6379) #redis or localhost

#test the redis dB
redisdB.set('foo', 'bar')
value = redisdB.get('foo')
if (value=='bar'):
    my_logger.info("Connected to Redis dB")
else:
    my_logger.error("Can not connect to Redis dB")
    raise Exception('Can not connect to Redis dB on port 6379')


connectionDict={} #holds a dictionary of DroneKit connection objects
connectionNameTypeDict={} #holds the additonal name, type and starttime for the conections
actionArrayDict={} #holds recent actions executied by each drone
authorizedZoneDict={} #holds zone authorizations for each drone
 
def applyHeadders():
    my_logger.debug('Applying HTTP headers')
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin',      '*')
    web.header('Access-Control-Allow-Credentials', 'true')        
    web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')   
    web.header('Access-Control-Allow-Headers', 'Content-Type')      
    return

def connectVehicle(inVehicleId):
    #global connectionStringArray
    global redisdB
    global connectionDict
    global actionArrayDict
    try:
        my_logger.debug( "connectVehicle called with inVehicleId = " + str(inVehicleId))
        #connectionString=connectionStringArray[inVehicleId]
        jsonObjStr=redisdB.get('connectionString:' + str(inVehicleId))
        my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
        jsonObj=json.loads(jsonObjStr)
        connectionString=jsonObj['connectionString']
        vehicleName=jsonObj['name']
        vehicleType=jsonObj['vehicleType']
        vehicleStartTime=jsonObj['startTime']
        currentTime = time.time()
        timeSinceStart=currentTime-vehicleStartTime
        my_logger.info("timeSinceStart= " + str(timeSinceStart) )
        if (timeSinceStart<120): #less than two mins so throw Exception
            my_logger.warn( "Raising warning")
            raise Warning('Vehicle starting up ' + inVehicleId) 

        my_logger.info("connection string for vehicle " + str(inVehicleId) + "='" + connectionString + "'")
        # Connect to the Vehicle.
        if not connectionDict.get(inVehicleId):
            my_logger.info("connectionString: %s" % (connectionString,))
            my_logger.info("Connecting to vehicle on: %s" % (connectionString,))
            connectionNameTypeDict[inVehicleId]={"name":vehicleName,"vehicleType":vehicleType}
            actionArrayDict[inVehicleId]=[] #create empty action array
            connectionDict[inVehicleId] = connect(connectionString, wait_ready=True, heartbeat_timeout=10)
            my_logger.info("actionArrayDict")
            my_logger.info(actionArrayDict)
        else:
            my_logger.debug( "Already connected to vehicle")
    except Warning:
        my_logger.warn( "Caught warning: Vehicle starting up")
        raise Warning('Vehicle starting up ' + inVehicleId)
    except Exception as e:
        my_logger.warn( "Caught exceptio: Unexpected error in connectVehicle:")
        my_logger.warn( "VehicleId="+str(inVehicleId))
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")   
        raise Exception('Unexpected error connecting to vehicle ' + str(inVehicleId)) 
    return connectionDict[inVehicleId]

def latLonAltObj(inObj):
    output={}
    output["lat"]=(inObj.lat)
    output["lon"]=(inObj.lon)
    output["alt"]=(inObj.alt)
    return output

def distanceInMeters(lat1,lon1,lat2,lon2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance*1000

#methods to support the different actions
def rtl(inVehicle):        
     
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Return-to-Launch"
        outputObj["status"]="success"
        #coodinates are same as home
        homeLocation=inVehicle.home_location
        outputObj["coordinate"]=[homeLocation.lat, homeLocation.lon, homeLocation.alt]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=20
        my_logger.info( "Returning to Launch")
        inVehicle.mode = VehicleMode("RTL")
    else:
        outputObj["name"]="Return-to-Launch"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
        my_logger.warn( "RTL error - Vehicle not armed")

    return outputObj  

def takeoff(inVehicle, inHeight):        
    outputObj={}
    if inVehicle.is_armable:
        outputObj["name"]="Takeoff"
        outputObj["height"]=inHeight
        outputObj["status"]="success"
        #coodinates are same as current + height
        currentLocation=inVehicle.location.global_relative_frame
        outputObj["coordinate"]=[currentLocation.lat, currentLocation.lon, inHeight]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=22
        my_logger.info( "Arming motors")
        # Copter should arm in GUIDED mode
        inVehicle.mode    = VehicleMode("GUIDED")
        inVehicle.armed   = True
        # Confirm vehicle armed before attempting to take off
        while not inVehicle.armed:
            my_logger.info( " Waiting for arming..."  )
            time.sleep(1)
        my_logger.info( "Taking off!")
        inVehicle.simple_takeoff(inHeight) # Take off to target altitude
    else:
        outputObj["name"] = "Takeoff"
        outputObj["status"] = "Error"
        outputObj["error"] = "vehicle not armable"
        my_logger.warn( "vehicle not armable")
    return outputObj

def auto(inVehicle):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Start-Mission"
        outputObj["status"]="success"
        my_logger.info( "Auto mission")
        if inVehicle.mode.name=="AUTO":
            #vehicle already in auto mode - swap it into GUIDED first.
            inVehicle.mode    = VehicleMode("GUIDED")
            time.sleep(1)
        inVehicle.mode = VehicleMode("AUTO")
    else:    
        outputObj["name"]="Start-Mission"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def land(inVehicle):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Land"
        outputObj["status"]="success"
        #coodinates are same as current 
        currentLocation=inVehicle.location.global_relative_frame
        outputObj["coordinate"]=[currentLocation.lat, currentLocation.lon, 0]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=23
        my_logger.info( "Landing")
        inVehicle.mode = VehicleMode("LAND")
    else:    
        outputObj["name"]="Land"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def goto(inVehicle, dNorth, dEast, dDown):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
    """
    global config
    outputObj={}
    if inVehicle.armed:
        distance=round(math.sqrt(dNorth*dNorth+dEast*dEast))
        my_logger.info("Goto a distance of " + str(distance) + "m.")
        if distance>1000:
            outputObj["status"]="Error"
            outputObj["error"]="Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            outputObj["name"]="Max-Distance-Error"
        else:
            outputObj["name"]="Goto-Relative-Current"
            outputObj["status"]="success"
            inVehicle.mode = VehicleMode("GUIDED")
            currentLocation = inVehicle.location.global_relative_frame
            targetLocation = get_location_metres(currentLocation, dNorth, dEast)
            targetLocation.alt=targetLocation.alt-dDown
            #coodinates are target
            outputObj["coordinate"]=[targetLocation.lat, targetLocation.lon, targetLocation.alt]
            outputObj["param1"]=0
            outputObj["param2"]=0
            outputObj["param3"]=0
            outputObj["param4"]=0
            outputObj["command"]=16
            inVehicle.simple_goto(targetLocation, groundspeed=10)
    else:    
        outputObj["name"]="Goto-Relative-Current"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.
    """
    my_logger.debug( "lat:" + str(original_location.lat) + " lon:" + str(original_location.lon))
    my_logger.debug( "north:" + str(dNorth) + " east:" + str(dEast))
     
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
    else:
        raise Exception("Invalid Location object passed")
    return targetlocation;

def gotoRelative(inVehicle, north, east, down):
    global config
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Goto-Relative-Home"
        outputObj["status"]="success"
        inVehicle.mode = VehicleMode("GUIDED")

        homeLocation=inVehicle.home_location

        #currentLocation = inVehicle.location.global_relative_frame
        targetLocation = get_location_metres(homeLocation, north, east)
        targetLocation.alt=homeLocation.alt-down
        distance=round(distanceInMeters(targetLocation.lat,targetLocation.lon,inVehicle.location.global_frame.lat,inVehicle.location.global_frame.lon))
        if distance>1000:
            outputObj["status"]="Error"
            outputObj["error"]="Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            outputObj["name"]="Max-Distance-Error"
        else:
            #coodinates are target
            outputObj["coordinate"]=[targetLocation.lat, targetLocation.lon, -down]
            outputObj["param1"]=0
            outputObj["param2"]=0
            outputObj["param3"]=0
            outputObj["param4"]=0
            outputObj["command"]=16  
            inVehicle.simple_goto(targetLocation, groundspeed=10)
    else:    
        outputObj["name"]="Goto-Relative-Home"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj


def gotoAbsolute(inVehicle, inLocation):        
    global config
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Goto-Absolute"
        outputObj["status"]="success"
        my_logger.debug( " Goto Location: %s" % inLocation   )  
        output = {"global_frame":inLocation}
        my_logger.debug( "lat" + str(inLocation['lat']))

        distance=round(distanceInMeters(inLocation['lat'], inLocation['lon'],inVehicle.location.global_frame.lat,inVehicle.location.global_frame.lon))
        if distance>1000:
            outputObj["status"]="Error"
            outputObj["error"]="Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            outputObj["name"]="Max-Distance-Error"
        else:
            inVehicle.mode = VehicleMode("GUIDED")
            #coodinates are target
            outputObj["coordinate"]=[inLocation['lat'], inLocation['lon'], inLocation['alt']]
            outputObj["param1"]=0
            outputObj["param2"]=0
            outputObj["param3"]=0
            outputObj["param4"]=0
            outputObj["command"]=16

            inVehicle.simple_goto(LocationGlobal(inLocation['lat'],inLocation['lon'],inLocation['alt']), groundspeed=10)
    else:    
        outputObj["name"]="Goto-Absolute"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def roi(inVehicle, inLocation):        
    outputObj={}
    outputObj["name"]="Region-of-Interest"
    outputObj["status"]="success"
    my_logger.debug( " Home Location: %s" % inLocation     )
    output = {"home_location":inLocation}
    my_logger.debug( "lat" + str(inLocation['lat']))
    #coodinates are target
    outputObj["coordinate"]=[inLocation['lat'],inLocation['lon'],inLocation['alt']]
    outputObj["param1"]=0
    outputObj["param2"]=0
    outputObj["param3"]=0
    outputObj["param4"]=0
    outputObj["command"]=80  
    set_roi(inVehicle, inLocation)
    return outputObj

def set_roi(inVehicle, location):
    # create the MAV_CMD_DO_SET_ROI command
    msg = inVehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
        0, #confirmation
        0, 0, 0, 0, #params 1-4
        location['lat'],
        location['lon'],
        location['alt']
        )
    # send command to vehicle
    inVehicle.send_mavlink(msg)

def getVehicleStatus(inVehicle):
    # inVehicle is an instance of the Vehicle class
    outputObj={}
    web.header('Content-Type', 'application/json')
    my_logger.debug( "Autopilot Firmware version: %s" % inVehicle.version)
    outputObj["version"]=str(inVehicle.version)
    my_logger.debug( "Global Location: %s" % inVehicle.location.global_frame)
    global_frame=latLonAltObj(inVehicle.location.global_frame)
    outputObj["global_frame"]=global_frame
    my_logger.debug( "Global Location (relative altitude): %s" % inVehicle.location.global_relative_frame)
    global_relative_frame=latLonAltObj(inVehicle.location.global_relative_frame)
    outputObj["global_relative_frame"]=global_relative_frame
    my_logger.debug( "Local Location: %s" % inVehicle.location.local_frame)    #NED
    local_frame={}
    local_frame["north"]=(inVehicle.location.local_frame.north)
    local_frame["east"]=(inVehicle.location.local_frame.east)
    local_frame["down"]=(inVehicle.location.local_frame.down)
    outputObj["local_frame"]=local_frame
    my_logger.debug( "Attitude: %s" % inVehicle.attitude)
    outputObj["attitude"]={"pitch":inVehicle.attitude.pitch,"roll":inVehicle.attitude.roll,"yaw":inVehicle.attitude.yaw}
    my_logger.debug( "Velocity: %s" % inVehicle.velocity)
    outputObj["velocity"]=(inVehicle.velocity)
    my_logger.debug( "GPS: %s" % inVehicle.gps_0)
    outputObj["gps_0"]={"eph":(inVehicle.gps_0.eph),"epv":(inVehicle.gps_0.eph),"fix_type":(inVehicle.gps_0.fix_type),"satellites_visible":(inVehicle.gps_0.satellites_visible)}
    my_logger.debug( "Groundspeed: %s" % inVehicle.groundspeed)
    outputObj["groundspeed"]=(inVehicle.groundspeed)
    my_logger.debug( "Airspeed: %s" % inVehicle.airspeed)
    outputObj["airspeed"]=(inVehicle.airspeed)
    my_logger.debug( "Gimbal status: %s" % inVehicle.gimbal)
    outputObj["gimbal"]={"pitch":inVehicle.gimbal.pitch,"roll":inVehicle.gimbal.roll,"yaw":inVehicle.gimbal.yaw}
    my_logger.debug( "Battery: %s" % inVehicle.battery)
    outputObj["battery"]={"voltage":inVehicle.battery.voltage,"current":inVehicle.battery.current,"level":inVehicle.battery.level}
    my_logger.debug( "EKF OK?: %s" % inVehicle.ekf_ok)
    outputObj["ekf_ok"]=(inVehicle.ekf_ok)
    my_logger.debug( "Last Heartbeat: %s" % inVehicle.last_heartbeat)
    outputObj["last_heartbeat"]=(inVehicle.last_heartbeat)
    my_logger.debug( "Rangefinder: %s" % inVehicle.rangefinder)
    outputObj["rangefinder"]={"distance":inVehicle.rangefinder.distance,"voltage":inVehicle.rangefinder.voltage}
    my_logger.debug( "Heading: %s" % inVehicle.heading)
    outputObj["heading"]=(inVehicle.heading)
    my_logger.debug( "Is Armable?: %s" % inVehicle.is_armable)
    outputObj["is_armable"]=(inVehicle.is_armable)
    my_logger.debug( "System status: %s" % inVehicle.system_status.state)
    outputObj["system_status"]=str(inVehicle.system_status.state)
    my_logger.debug( "Mode: %s" % inVehicle.mode.name  )  # settable
    outputObj["mode"]=str(inVehicle.mode.name)
    my_logger.debug( "Armed: %s" % inVehicle.armed  )  # settable    
    outputObj["armed"]=(inVehicle.armed)


    return outputObj

def updateActionStatus(inVehicle, inVehicleId):
    #test to see whether the vehicle is at the target location of the action
    my_logger.info("############# in updateActionStatus")

    my_logger.info("inVehicleId")
    my_logger.info(inVehicleId)
    my_logger.info("actionArrayDict")
    my_logger.info(actionArrayDict)
    my_logger.info("#############")

    actionArray=actionArrayDict[inVehicleId]


    my_logger.info(actionArray)

    if (len(actionArray)>0):
        latestAction=actionArray[len(actionArray)-1]

        if (latestAction['action']['status']=="Error"):
            latestAction['complete']=False
            latestAction['completeStatus']='Error'
            return
        my_logger.debug("Latest Action:" + latestAction['action']['name'])

        if (latestAction['action']['name']=='Start-Mission'):
            #cant monitor progress at the moment
            my_logger.info("Cant monitor progress for mission")
        else:
            my_logger.debug("Monitoring progress for action '" + latestAction['action']['name'] + "'")

            targetCoordinates=latestAction['action']['coordinate'] #array with lat,lon,alt
            my_logger.info(inVehicle)
            vehicleCoordinates=inVehicle.location.global_relative_frame #object with lat,lon,alt attributes
            #Return-to-launch uses global_frame (alt is absolute)
            
            if (latestAction['action']['name']=='Return-to-Launch'):
                vehicleCoordinates=inVehicle.location.global_frame #object with lat,lon,alt attributes

            horizontalDistance=distanceInMeters(targetCoordinates[0],targetCoordinates[1],vehicleCoordinates.lat,vehicleCoordinates.lon)
            verticalDistance=abs(targetCoordinates[2]-vehicleCoordinates.alt)
            latestAction['horizontalDistance']=round(horizontalDistance,2)
            latestAction['verticalDistance']=round(verticalDistance,2)
            if ((horizontalDistance<5) and (verticalDistance<1)):
                latestAction['complete']=True
                latestAction['completeStatus']='Complete'
            else:
                latestAction['completeStatus']='In progress'
                latestAction['complete']=False
            #region of interest is special case
            if (latestAction['action']['name']=='Region-of-Interest'):
                latestAction['complete']=True
                latestAction['completeStatus']='Complete'

    if (len(actionArray)>1): #check if previous actions completed or were interrupted
        previousAction=actionArray[len(actionArray)-2]
        if (previousAction.get('complete',False)==False):
            if (previousAction.get('completeStatus','In progress')=="In progress"):
                previousAction['completeStatus']='Interrupted'
                previousAction['complete']=False

           

    return

class index:        
    def GET(self):
        try:
            my_logger.info( "#### Method GET of index #####")
            applyHeadders()
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


class vehicleIndex:        
    def GET(self):
        try:
            global redisdB
            my_logger.info( "#### Method GET of vehicleIndex #####")
            applyHeadders()
            outputObj=[]

            keys=redisdB.keys("connectionString:*")
            for key in keys:
                my_logger.debug( "key = '"+key+"'")
                jsonObjStr=redisdB.get(key)
                my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
                jsonObj=json.loads(jsonObjStr)
                connectionString=jsonObj['connectionString']
                vehicleName=jsonObj['name']
                vehicleType=jsonObj['vehicleType']
                droneId=key[17:]

                outputObj.append( {"_links":{"self":{"href":homeDomain+"/vehicle/"+str(droneId),"title":"Get status for vehicle " + str(droneId)}},
                        "id":str(droneId),"name":vehicleName,"vehicleType":vehicleType})

            actions='[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). The connectionString is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + homeDomain+ '/vehicle",\n"fields":[{"name":"vehicleType", "type":{"listOfValues":["simulated","real"]}}, {"name":"connectionString","type":"string"}, {"name":"name","type":"string"}] }]\n'
            self={"self":{"title":"Return the collection of available vehicles.","href": homeDomain+"/vehicle" }}
            my_logger.debug("actions")
            my_logger.debug(actions)
            jsonResponse='{"_embedded":{"vehicle":'+json.dumps(outputObj)+'},"_actions":'+actions+',"_links":'+ json.dumps(self)+'}'
            my_logger.debug("jsonResponse")
            my_logger.debug(jsonResponse)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
                            
        return jsonResponse

    def POST(self):
        global redisdB
        global config
        try:
            my_logger.info( "#### Method POST of vehicleIndex #####")
            applyHeadders()
            dataStr=web.data()
            my_logger.info( dataStr)            
            data = json.loads(dataStr)
            droneType=data["vehicleType"]
            vehicleName=data["name"]
            connection=None
            if (droneType=="simulated"):
                #build simulted drone using aws

                #test how many non-terminated instances there are
                ec2client = boto3.client('ec2')
                response = ec2client.describe_instances()
                #print(response)
                instances=[]

                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        # This sample print will output entire Dictionary object
                        #print(instance)
                        # This will print will output the value of the Dictionary key 'InstanceId'
                        if (instance["State"]["Name"]!="terminated"):
                            instances.append(instance["InstanceId"])
                            
                my_logger.debug("Non terminated instances=")
                my_logger.debug(len(instances))
                if (len(instances)>20):
                    outputObj={}
                    outputObj["status"]="Error: can't launch more than "+str(20)+" drones"
                    return json.dumps(outputObj)


                my_logger.info("Creating new AWS image")
                ec2resource = boto3.resource('ec2')
                createresponse=ec2resource.create_instances(ImageId='ami-5be0f43f', MinCount=1, MaxCount=1,InstanceType='t2.micro',SecurityGroupIds=['sg-fd0c8394'])
                my_logger.info(createresponse[0].private_ip_address)
                connection="tcp:" + str(createresponse[0].private_ip_address) + ":14550"
            else:
                connection = data["connectionString"]
            
            my_logger.debug( connection)

            uuidVal=uuid.uuid4()
            key=str(uuidVal)[:8]
            my_logger.info("adding connectionString to Redis db with key '"+"connectionString:"+str(key)+"'")
            redisdB.set("connectionString:"+key,json.dumps({"connectionString":connection,"name":vehicleName,"vehicleType":droneType,"startTime":time.time()}))

            #connectionStringArray.append(connection)
            #connectionDict.append(None)
            #authorizedZoneDict.append({})
            outputObj={}
            outputObj["connection"]=connection
            outputObj["id"]=key
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)

    def OPTIONS(self):
        try:
            my_logger.info( "#### OPTIONS of vehicleIndex - just here to suppor the CORS Cross-Origin security #####")
            applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


class action:     
    def OPTIONS(self, vehicleId):
        try:
            my_logger.info( "#### Method OPTIONS of action - just here to suppor the CORS Cross-Origin security ####")
            applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of action ####")

            applyHeadders()
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 

            vehicleStatus=getVehicleStatus(inVehicle)
            outputObj={}
            outputObj["_links"]={"self":{"href":homeDomain+"/vehicle/"+str(vehicleId)+"/action","title":"Get the actions for this vehicle."}}
            availableActions=[]
            #available when armed
            if vehicleStatus["armed"]:
                availableActions.append({   
                    "name":"Region-of-Interest",
                    "title":"Set a Region of Interest : When the drone is flying, it will face the point  <lat>,<lon>,<alt> (defaults to the home location)",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Region-of-Interest"},{"name":"lat","type":"float","value":51.3946},{"name":"lon","type":"float","value":-1.299},{"name":"alt","type":"float","value":105}]
                })
                availableActions.append({   
                    "name":"Land",
                    "title":"Land at current location",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Land"}]
                })
                availableActions.append({   
                    "name":"Return-to-Launch",
                    "title":"Return to launch: Return to the home location and land.",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Return-to-Launch"}]
                })
                availableActions.append({   
                    "name":"Start-Mission",
                    "title":"Begin the pre-defined mission.",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Start-Mission"}]
                })
                availableActions.append({   
                    "name":"Goto-Absolute",
                    "title":"Go to the location at latitude <lat>, longitude <lon> and altitude <alt> (above sea level).",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Goto-Absolute"},{"name":"lat","type":"float","value":51.3946},{"name":"lon","type":"float","value":-1.299},{"name":"alt","type":"float","value":105}]
                })
                availableActions.append({   
                    "name":"Goto-Relative-Home",
                    "title":"Go to the location <north> meters North, <east> meters East and <up> meters vertically from the home location.",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Goto-Relative-Home"},{"name":"north","type":"float","value":30},{"name":"east","type":"float","value":30},{"name":"up","type":"float","value":10}]
                })
                availableActions.append({   
                    "name":"Goto-Relative-Current",
                    "title":"Go to the location <north> meters North, <east> meters East and <up> meters vertically from the current location.",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Goto-Relative-Current"},{"name":"north","type":"float","value":30},{"name":"east","type":"float","value":30},{"name":"up","type":"float","value":10}]
                })
            else :
                availableActions.append({   
                    "name":"Takeoff",
                    "title":"Arm and takeoff in GUIDED mode to height of <height> (default 20m).",
                    "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Takeoff"},{"name":"height","type":"float","value":30}]
                })
            outputObj['_actions']=availableActions
            my_logger.debug(outputObj)
            updateActionStatus(inVehicle, vehicleId);
            outputObj['actions']=actionArrayDict[vehicleId]
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info( "#### Method POST of action ####")
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up ", "_actions": actions}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId), "_actions": actions}) 
            applyHeadders()
            data = json.loads(web.data())
            #get latest data (inc homeLocation from vehicle)
            my_logger.debug( "Getting commands:")

            cmds = inVehicle.commands
            my_logger.debug( "Download:")

            cmds.download()
            my_logger.debug( "Wait until ready:")
            cmds.wait_ready() 


            my_logger.debug( "Data:")
            my_logger.debug( data)
            value = data["name"]
            my_logger.debug( "Value:")
            my_logger.debug( value)
            outputObj={}
            if value=="Return-to-Launch":
                outputObj["action"]=rtl(inVehicle)
            elif value=="Takeoff":
                height=data.get("height",20) #get height - default to 20
                my_logger.debug( "Taking off to height of " + str(height))
                outputObj["action"]=takeoff(inVehicle,height)
            elif value=="Start-Mission":
                outputObj["action"]=auto(inVehicle)
            elif value=="Land":
                outputObj["action"]=land(inVehicle)
            elif value=="Goto-Absolute":
                defaultLocation=inVehicle.location.global_frame #default to current position
                my_logger.debug( "Global Frame" + str(defaultLocation))
                inLat=data.get("lat",defaultLocation.lat)
                inLon=data.get("lon",defaultLocation.lon)
                inAlt=data.get("alt",defaultLocation.alt)
                locationObj={'lat':float(inLat), 'lon':float(inLon), 'alt':float(inAlt)}
                outputObj["action"]=gotoAbsolute(inVehicle,locationObj)
            elif value=="Goto-Relative-Home":
                inNorth=float(data.get("north",0))
                inEast=float(data.get("east",0))
                inDown=-float(data.get("up",0))
                my_logger.debug( "Goto-Relative-Home" )
                my_logger.debug( inNorth)
                my_logger.debug( inEast)
                my_logger.debug( inDown)
                outputObj["action"]=gotoRelative(inVehicle,inNorth,inEast,inDown)
            elif value=="Goto-Relative-Current":
                inNorth=float(data.get("north",0))
                inEast=float(data.get("east",0))
                inDown=-float(data.get("up",0))
                outputObj["action"]=goto(inVehicle,inNorth,inEast,inDown)
            elif value=="Region-of-Interest":
                cmds = inVehicle.commands
                cmds.download()
                cmds.wait_ready()
                defaultLocation=inVehicle.home_location
                inLat=data.get("lat",defaultLocation.lat)
                inLon=data.get("lon",defaultLocation.lon)
                inAlt=data.get("alt",defaultLocation.alt)
                locationObj={'lat':float(inLat), 'lon':float(inLon), 'alt':float(inAlt)}
                outputObj["action"]=roi(inVehicle,locationObj)
            else:
                outputObj["action"]={"status":"error", "name":value, "error":"No action found with name '" + value+ "'." }
            actionArray=actionArrayDict[vehicleId]
            if (len(actionArray)==0):
                outputObj['action']['id']=0;
            else:
                outputObj['action']['id']=actionArray[len(actionArray)-1]['action']['id']+1
            actionArray.append(outputObj)
            if (len(actionArray)>10):
                actionArray.pop(0)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             


        return json.dumps(outputObj)

def getMissionActions(vehicleId) :
    try:
        try:
            inVehicle=connectVehicle(vehicleId)   
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
        except Exception:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
        vehicleStatus=getVehicleStatus(inVehicle)
        outputObj={"_actions":[{"name":"upload mission","method":"POST","title":"Upload a new mission to the vehicle. The mission is a collection of mission actions with <command>, <coordinate[lat,lon,alt]> and command specific <param1>,<param2>,<param3>,<param4>. The command-set is described at https://pixhawk.ethz.ch/mavlink/", 
                "fields": [{"name":"coordinate", "type":"array","value":[51.3957,-1.3441,30]},{"name":"command","type":"integer","value":16},
                {"name":"param1","type":"integer"},{"name":"param2","type":"integer"},{"name":"param3","type":"integer"},{"name":"param4","type":"integer"}]}]}
        cmds = inVehicle.commands
        cmds.download()
        cmds.wait_ready()
        my_logger.debug( "Mission Commands")
        # Save the vehicle commands to a list
        missionlist=[]
        for cmd in cmds:
            autoContinue=True
            if (cmd.autocontinue==0):
                autoContinue=False
            missionlist.append({'id':cmd.seq,"autoContinue": autoContinue ,"command": cmd.command,"coordinate": [cmd.x,cmd.y,cmd.z],'frame':cmd.frame,'param1':cmd.param1,'param2':cmd.param2,'param3':cmd.param3,'param4':cmd.param4})
            my_logger.debug( cmd)
        my_logger.debug( missionlist)
        outputObj['items']=missionlist
        outputObj['plannedHomePosition']={'id':0,'autoContinue':True,'command':16,"coordinate": [inVehicle.home_location.lat,inVehicle.home_location.lon,0], 'frame':0,'param1':0,'param2':0,'param3':0,'param4':0}
        outputObj['version']='1.0'
        outputObj['MAV_AUTOPILOT']=3
        outputObj['complexItems']=[]
        outputObj['groundStation']='QGroundControl'
        outputObj["_links"]={"self":{"href":homeDomain+"/vehicle/"+str(vehicleId)+"/mission","title":"Get the current mission commands from the vehicle."}}

        #outputObj['mission']=cmds
        output=json.dumps(outputObj)   
    except Exception as e: 
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")   
        return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
    return output

class mission:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of mission ####")
            my_logger.debug( "vehicleId = '"+vehicleId+"'")
            applyHeadders()
            output=getMissionActions(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info( "#### Method POST of mission ####")
            applyHeadders()
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            #download existing commands
            my_logger.info( "download existing commands")
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            #clear the commands
            my_logger.info( "clearing existing commands")
            cmds.clear()
            inVehicle.flush()
            missionActionArray = json.loads(web.data())
            my_logger.info( "missionCommandArray:")
            my_logger.info( missionActionArray)
            #add new commands
            for missionAction in missionActionArray:
                my_logger.info(missionAction)
                lat = missionAction['coordinate'][0]
                lon = missionAction['coordinate'][1]
                altitude = missionAction['coordinate'][2]
                cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, missionAction['command'],
                    0, 0, missionAction['param1'], missionAction['param2'], missionAction['param3'], missionAction['param4'],
                    lat, lon, altitude)
                my_logger.info( "Add new command with altitude:")
                my_logger.info( altitude)
                cmds.add(cmd)
            inVehicle.flush()
            my_logger.info( "Command added")
            output=getMissionActions(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self, vehicleId):
        try:
            my_logger.info( "#### Method OPTIONS of mission - just here to suppor the CORS Cross-Origin security ####")
            applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


class authorizedZone:        

    def POST(self,vehicleId):
        try:
            my_logger.info( "#### Method POST of authorizedZone ####")
            my_logger.debug( "vehicleId = '"+vehicleId+"'")
            applyHeadders()
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            vehicleStatus=getVehicleStatus(inVehicle)
            my_logger.info(vehicleStatus)
            data = json.loads(web.data())
            zone = data["zone"]
            #validate and enrich data
            if (zone["shape"]["name"]=="circle"):
                if (zone.get("lat",-1)==-1): #if there is no lat,lon add current location as default
                    zone["shape"]["lat"]=vehicleStatus["global_frame"]["lat"]
                    zone["shape"]["lon"]=vehicleStatus["global_frame"]["lon"]
            outputObj={}
            outputObj["zone"]=zone
            authorizedZoneDict[vehicleId]=zone
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)


def getSimulatorParams(vehicleId) :
    try:
        try:
            inVehicle=connectVehicle(vehicleId)   
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
        except Exception:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
        vehicleStatus=getVehicleStatus(inVehicle)
        outputObj={"_actions":[{"method":"POST","title":"Upload a new simulator paramater to the simulator. ", "fields":[ {"name":"parameter","value":"SIM_WIND_SPD","type":"string"},{"name":"value","type":"integer","float":10}]}]};

        simulatorParams={}

        my_logger.debug( "Simulator Parameters")
        my_logger.debug( inVehicle.parameters)

        for key, value in inVehicle.parameters.iteritems():
            my_logger.debug( " Key:"+str(key)+" Value:" + str(value))
            my_logger.debug( key.find("SIM"))
            if (key.find("SIM")==0):
                simulatorParams[key]=inVehicle.parameters[key]

        outputObj['simulatorParams']=simulatorParams
        outputObj["_links"]={"self":{"href":homeDomain+"/vehicle/"+str(vehicleId)+"/simulator","title":"Get the current simulator parameters from the vehicle."},
            "up":{"href":homeDomain+"/vehicle/"+str(vehicleId),"title":"Get status for parent vehicle."}}


 
        #outputObj['mission']=cmds
        output=json.dumps(outputObj)   
    except Exception as e: 
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")   
        return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
    return output


class simulator:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of simulator ####")
            my_logger.debug( "vehicleId = '"+vehicleId+"'")
            applyHeadders()
            output=getSimulatorParams(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info( "#### Method POST of simulator ####")
            applyHeadders()
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            my_logger.info( "posting new simulator parameter")
            simulatorData = json.loads(web.data());
            my_logger.info(simulatorData);
            simKey=str(simulatorData['parameter'])
            simValue=simulatorData['value']
            my_logger.info(simKey);
            my_logger.info(simValue);
            inVehicle.parameters[simKey]=simValue;
            my_logger.info('Updated parameter');
           
            output=getSimulatorParams(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self, vehicleId):
        try:
            my_logger.info( "#### Method OPTIONS of simulator - just here to suppor the CORS Cross-Origin security ####")
            applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output



class homeLocation:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of homeLocation ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            applyHeadders()
            outputObj={}
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            vehicleStatus=getVehicleStatus(inVehicle)
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            my_logger.debug( " Home Location: %s" % inVehicle.home_location     )
            output = json.dumps({"_links":{"self":{"href":homeDomain+"/vehicle/"+str(vehicleId)+"/homeLocation","title":"Get the home location for this vehicle"}},"home_location":latLonAltObj(inVehicle.home_location)}   )   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


class vehicleStatus:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of vehicleStatus ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            applyHeadders()
            outputObj={}

            actions=[{"method":"DELETE","href":homeDomain+"/vehicle/"+str(vehicleId),"title":"Delete connection to vehicle " + str(vehicleId)}]

            #test if vehicleId is an integer 1-4
            #try:
            #    vehId=int(vehicleId)
            #except ValueError:
            #    stringArray=vehicleId.split('/')
            #    vehicleId=stringArray[0]
            #    statusVal=stringArray[1]
            #my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            try:
                inVehicle=connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up ", "_actions": actions}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                jsonObjStr=redisdB.get('connectionString:' + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId) + "with connection " + jsonObjStr, "_actions": actions}) 
            vehicleStatus=getVehicleStatus(inVehicle)
            vehicleStatus["name"]=connectionNameTypeDict[vehicleId]['name']
            vehicleStatus["vehicleType"]=connectionNameTypeDict[vehicleId]['vehicleType']

            vehicleStatus["zone"]=authorizedZoneDict.get(vehicleId)
            if not vehicleStatus["zone"]: #if no authorizedZone then set default
                vehicleStatus["zone"]={"shape":{"name":"circle","lat":vehicleStatus["global_frame"]["lat"],"lon":vehicleStatus["global_frame"]["lon"]}}


            #check if vehicle still in zone
            distance=distanceInMeters(vehicleStatus["zone"]["shape"]["lat"],vehicleStatus["zone"]["shape"]["lon"],vehicleStatus["global_frame"]["lat"],vehicleStatus["global_frame"]["lon"])
            if (distance>500):
                rtl(inVehicle)


            vehicleStatus['id']=vehicleId
            vehicleStatus['_links']={};
            vehicleStatus['_links']["self"]={"href": homeDomain+"/vehicle/"+str(vehicleId)+"/", "title":"Get status for vehicle "+str(vehicleId)+"."}
            vehicleStatus['_links']['homeLocation']={"href":homeDomain + "/vehicle/" + str(vehicleId) + "/homeLocation","title":"Get the home location for this vehicle"}
            vehicleStatus['_links']['action']={"href":homeDomain+ "/vehicle/" + str(vehicleId) +"/action","title":"Get the actions  for this vehicle."}
            vehicleStatus['_links']['mission']={"href":homeDomain+ "/vehicle/" + str(vehicleId) +"/mission","title":"Get the current mission commands from the vehicle."}
            vehicleStatus['_links']['simulator']={"href":homeDomain+ "/vehicle/" + str(vehicleId) +"/simulator","title":"Get the current simulator parameters from the vehicle."}
            output=""
            if statusVal=="/":
                statusVal=""            
            if statusVal=="":
                outputObj=vehicleStatus
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
            elif statusVal=="homelocation":
                cmds = inVehicle.commands
                cmds.download()
                cmds.wait_ready()
                my_logger.debug( " Home Location: %s" % inVehicle.home_location     )
                output = json.dumps({"home_location":latLonAltObj(inVehicle.home_location)}   )   
            elif statusVal=="action":
                outputObj={"error":"Use "+homeDomain+"/vehicle/1/action  (with no / at the end)."}
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
            else:
                statusLen=len(statusVal)
                my_logger.debug( statusLen)
                #statusVal=statusVal[1:]
                my_logger.debug( statusVal)
                outputObj={statusVal: vehicleStatus.get(statusVal,{"error":"Vehicle status '"+statusVal+"' not found. Try getting all using "+homeDomain+"/vehicle/"+vehicleId+"/"})}
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def DELETE(self, vehicleId):
        try:
            my_logger.info( "#### Method DELETE of vehicleStatus ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            applyHeadders()

            jsonObjStr=redisdB.get('connectionString:' + str(vehicleId))
            my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
            jsonObj=json.loads(jsonObjStr)
            connectionString=jsonObj['connectionString']
            ipAddress=connectionString[4:-6]


            try:
                #terminate any AWS instances with that private IP address
                ec2client = boto3.client('ec2')
                response = ec2client.describe_instances()
                #print(response)
                instances=[]

                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        # This sample print will output entire Dictionary object
                        #print(instance)
                        # This will print will output the value of the Dictionary key 'InstanceId'
                        if (instance["State"]["Name"]!="terminated"):
                            if (instance.get("PrivateIpAddress",None)==ipAddress):
                                #my_logger.debug(instance)
                                my_logger.debug(instance["PrivateIpAddress"],instance["InstanceId"],instance["InstanceType"],instance["State"]["Name"])
                                instances.append(instance["InstanceId"])
                            
                my_logger.debug("instances to terminate")
                my_logger.debug(instances)

                if (len(instances)>0):  
                    #startresp=ec2client.start_instances(InstanceIds=["i-094270016448e61e2"])
                    stopresp=ec2client.terminate_instances(InstanceIds=instances)
                    my_logger.debug("Terminated instance")

            except Exception as inst:
                my_logger.error( "Error conneting to AWS:")
                my_logger.error( "VehicleId=")
                my_logger.error( vehicleId)
                my_logger.error( "Exception=")
                my_logger.error( inst)
                #ignore error and continue


            my_logger.info("connectionString="+connectionString)
            my_logger.info("ipAddress="+ipAddress)
            redisdB.delete("connectionString:"+vehicleId)
            connectionDict.pop("connectionString:"+vehicleId, None)

            outputObj={"status":"success"}
            output = json.dumps(outputObj)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self,vehicleId):
        try:
            my_logger.info( "#### OPTIONS of vehicleStatus - just here to suppor the CORS Cross-Origin security #####")
            applyHeadders()

            outputObj={}
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
            applyHeadders()
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
            applyHeadders()
            outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)


urls = (
    '/', 'index',
    '/vehicle/(.*)/action', 'action',
    '/vehicle/(.*)/homeLocation', 'homeLocation',
    '/vehicle/(.*)/mission', 'mission',
    '/vehicle/(.*)/authorizedZone', 'authorizedZone',
    '/vehicle/(.*)/simulator', 'simulator',
    '/vehicle', 'vehicleIndex',
    '/vehicle/(.*)', 'vehicleStatus', #was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
    '/(.*)', 'catchAll'
)

homeDomain = os.getenv('HOME_DOMAIN', defaultHomeDomain)
my_logger.debug( "Home Domain:"  + homeDomain)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()





