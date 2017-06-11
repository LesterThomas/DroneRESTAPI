#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math
import droneAPIMain, droneAPIUtils

my_logger = droneAPIMain.my_logger

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
        jsonObjStr=droneAPIMain.redisdB.get('connectionString:' + str(inVehicleId))
        my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
        jsonObj=json.loads(jsonObjStr)
        connectionString=jsonObj['connectionString']
        vehicleName=jsonObj['name']
        vehicleType=jsonObj['vehicleType']
        vehicleStartTime=jsonObj['startTime']
        currentTime = time.time()
        timeSinceStart=currentTime-vehicleStartTime
        my_logger.info("timeSinceStart= " + str(timeSinceStart) )
        if (timeSinceStart<10): #less than 10 seconds so throw Exception
            my_logger.warn( "Raising warning")
            raise Warning('Vehicle starting up ' + inVehicleId) 

        my_logger.info("connection string for vehicle " + str(inVehicleId) + "='" + connectionString + "'")
        # Connect to the Vehicle.
        if not droneAPIMain.connectionDict.get(inVehicleId):
            my_logger.info("connectionString: %s" % (connectionString,))
            my_logger.info("Connecting to vehicle on: %s" % (connectionString,))
            droneAPIMain.connectionNameTypeDict[inVehicleId]={"name":vehicleName,"vehicleType":vehicleType}
            droneAPIMain.actionArrayDict[inVehicleId]=[] #create empty action array
            droneAPIMain.connectionDict[inVehicleId] = connect(connectionString, wait_ready=True, heartbeat_timeout=10)
            my_logger.info("droneAPIMain.actionArrayDict")
            my_logger.info(droneAPIMain.actionArrayDict)
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
    return droneAPIMain.connectionDict[inVehicleId]


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


def getVehicleStatus(inVehicle):
    # inVehicle is an instance of the Vehicle class
    outputObj={}
    web.header('Content-Type', 'application/json')
    my_logger.debug( "Autopilot Firmware version: %s" % inVehicle.version)
    outputObj["version"]=str(inVehicle.version)
    my_logger.debug( "Global Location: %s" % inVehicle.location.global_frame)
    global_frame=droneAPIUtils.latLonAltObj(inVehicle.location.global_frame)
    outputObj["global_frame"]=global_frame
    my_logger.debug( "Global Location (relative altitude): %s" % inVehicle.location.global_relative_frame)
    global_relative_frame=droneAPIUtils.latLonAltObj(inVehicle.location.global_relative_frame)
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


