#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, watchtower, traceback, json, time, math, os, redis, docker

#define global variables
my_logger = None
connectionDict=None
connectionNameTypeDict=None
actionArrayDict=None
authorizedZoneDict=None 
defaultDockerHost=""
dronesimImage=""
homeDomain=""

redisdB = None


def startup():
    global homeDomain, dronesimImage, defaultDockerHost, connectionDict, connectionNameTypeDict, actionArrayDict, authorizedZoneDict, redisdB, my_logger

    #Set logging framework
    main_logger = logging.getLogger("DroneAPIServer")
    LOG_FILENAME = 'droneapi.log'
    main_logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    main_logger.addHandler(handler)
    main_logger.propegate=False

    try:
    	main_logger.addHandler(watchtower.CloudWatchLogHandler())
    except:
    	main_logger.warn("Can not add CloudWatch Log Handler")

    my_logger = logging.getLogger("DroneAPIServer."+str(__name__))


    my_logger.info("##################################################################################")
    my_logger.info("Starting DroneAPI at  "+str(time.time()))
    my_logger.info("##################################################################################")
    my_logger.info("Logging level:"+str(logging.INFO))

    #Set environment variables
    homeDomain=getEnvironmentVariable('DRONEAPI_URL')
    dronesimImage=getEnvironmentVariable('DOCKER_DRONESIM_IMAGE')
    defaultDockerHost=getEnvironmentVariable('DOCKER_HOST_IP')

    #set global variables
    connectionDict={} #holds a dictionary of DroneKit connection objects
    connectionNameTypeDict={} #holds the additonal name, type and starttime for the conections
    actionArrayDict={} #holds recent actions executied by each drone
    authorizedZoneDict={} #holds zone authorizations for each drone
    redisdB = redis.Redis(host='redis', port=6379) #redis or localhost

    #refresh the running containers based on redis data
    validateAndRefreshContainers(redisdB)

    return


def getEnvironmentVariable(inVariable):
    try:
        envVariable=os.environ[inVariable]
        my_logger.info("Env variable "+inVariable+"="+envVariable)
        return envVariable
    except Exception as e: 
        my_logger.error("Can't get environment variable "+inVariable)
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n") 
        my_logger.exception(traceLines)
    return ""

def validateAndRefreshContainers(redisdB):
    #test the redis dB
    #remove any old entries (and any old docker containers)
    my_logger.info("Connecting to Redis dB and removing any existing entries and stopping any existing containers at "+str(time.time()))

    dockerHostsArray=[]
    redisdB.set('foo', 'bar')
    my_logger.info("RedisSet "+str(time.time()))

    value = redisdB.get('foo')
    my_logger.info("RedisGet "+str(time.time()))
    if (value=='bar'):
        my_logger.info("Connected to Redis dB")
    else:
        my_logger.error("Can not connect to Redis dB")
        raise Exception('Can not connect to Redis dB on port 6379')

    #print out the relavant redisdB data
    #droneObjKeys=redisdB.keys("connectionString:*")
    #for key in droneObjKeys:
    #    jsonObjStr=redisdB.get(key)
    #    my_logger.info( "removing key = '"+key+"'" + ",redisDbObj = '"+jsonObjStr+"'")
    #    redisdB.delete(key)
    dockerHostsString=redisdB.get("dockerHostsArray")
    dockerHostsArray=None
    if (dockerHostsString==None):
    	dockerHostsArray=[{"internalIP":defaultDockerHost,"usedPorts":[]}]
    else :
    	dockerHostsArray=json.loads(dockerHostsString)
    	
    my_logger.info("dockerHostsArray fron Redis before validation")
    my_logger.info(dockerHostsArray)

    #check that I can access Docker on each host and to delete any existing containers
    index=-1
    for dockerHost in dockerHostsArray:
        index=index+1
        canAccessHost=True
        try :
            my_logger.info( "dockerHost = '"+dockerHost['internalIP']+"'")
            dockerClient = docker.DockerClient(version='1.27',base_url='tcp://'+dockerHost['internalIP']+':4243') #docker.from_env(version='1.27') 

            for container in dockerClient.containers.list():
                imageName=str(container.image)
                my_logger.info(container.id + " "+ container.name + " '" + imageName +"'")
                if (imageName=="<Image: '"+dronesimImage+"'>"):
                    my_logger.warn("stopping container "+container.id )
                    container.stop()
                    dockerClient.containers.prune(filters=None)

            #restart all the docker containers based on the usedPorts
            for port in dockerHost['usedPorts']:
                dockerContainer=dockerClient.containers.run(dronesimImage, detach=True, ports={'14550/tcp': port} )
                dockerContainerId=dockerContainer.id
                my_logger.info( "New container for port "+str(port)+"=" + str(dockerContainerId))




        except Exception as e: 
            my_logger.warn( "Can not connect to host: "+ str(dockerHost['internalIP']))
            canAccessHost=False
            dockerHostsArray.pop(index)
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n") 
            my_logger.exception(traceLines)
    
    my_logger.info("dockerHostsArray")
    my_logger.info(dockerHostsArray)

    if (len(dockerHostsArray)==0):
        my_logger.warn( "Docker host array is empty: adding default: "+ defaultDockerHost)
        dockerHostsArray=[{"internalIP":defaultDockerHost,"usedPorts":[]}]

    #add the updated dockerHostArray to Redis    
    redisdB.set("dockerHostsArray",json.dumps(dockerHostsArray))
    
    return    

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
        my_logger.info("Redis returns '"+str(jsonObjStr)+"'")
        if (jsonObjStr is None):
            my_logger.info("Raising Vehicle not found warning")
            raise Warning('Vehicle not found ') 
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
            my_logger.warn( "Raising Vehicle starting up warning")
            raise Warning('Vehicle starting up ') 

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
    except Warning as w:
        my_logger.warn( "Caught warning: "+ str(w))
        raise Warning(str(w))
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


print("Starting up at "+str(time.time()))
startup()