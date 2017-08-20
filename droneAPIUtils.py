"""This module has utility functions used by all the other modules in this App"""
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command, mavutil, APIException

import web
import logging
import watchtower
import traceback
import json
import time
import math
import os
import uuid
import redis
import docker

import droneAPIAction
# define global variables
my_logger = None
connectionDict = None
connectionNameTypeDict = None
actionArrayDict = None
authorizedZoneDict = None
defaultDockerHost = ""
dronesimImage = ""
homeDomain = ""
redisdB = None


def initaliseLogger():
    global my_logger

    # Set logging framework
    main_logger = logging.getLogger("DroneAPIServer")
    LOG_FILENAME = 'droneapi.log'
    main_logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    main_logger.addHandler(handler)
    main_logger.propegate = False

    try:
        main_logger.addHandler(watchtower.CloudWatchLogHandler())
    except BaseException:
        main_logger.warn("Can not add CloudWatch Log Handler")

    my_logger = logging.getLogger("DroneAPIServer." + str(__name__))

    my_logger.info("##################################################################################")
    my_logger.info("Starting DroneAPI at  " + str(time.time()))
    my_logger.info("##################################################################################")
    my_logger.info("Logging level:" + str(logging.INFO))

    return


def initaliseGlobals():
    global homeDomain, dronesimImage, defaultDockerHost, connectionDict, connectionNameTypeDict, actionArrayDict, authorizedZoneDict

    # Set environment variables
    homeDomain = getEnvironmentVariable('DRONEAPI_URL')
    dronesimImage = getEnvironmentVariable('DOCKER_DRONESIM_IMAGE')
    defaultDockerHost = getEnvironmentVariable('DOCKER_HOST_IP')

    # set global variables
    connectionDict = {}  # holds a dictionary of DroneKit connection objects
    connectionNameTypeDict = {}  # holds the additonal name, type and starttime for the conections
    actionArrayDict = {}  # holds recent actions executied by each drone
    authorizedZoneDict = {}  # holds zone authorizations for each drone

    return


def initiliseRedisDB():

    global redisdB
    redisdB = redis.Redis(host='redis', port=6379)  # redis or localhost

    return


def getEnvironmentVariable(inVariable):
    try:
        envVariable = os.environ[inVariable]
        my_logger.info("Env variable " + inVariable + "=" + envVariable)
        return envVariable
    except Exception as e:
        my_logger.error("Can't get environment variable " + inVariable)
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")
        my_logger.exception(traceLines)
    return ""


def validateAndRefreshContainers():
    try:
        # test the redis dB
        # remove any old entries (and any old docker containers)
        my_logger.info("Connecting to Redis dB and removing any existing entries and stopping any existing containers at " + str(time.time()))

        dockerHostsArray = []
        redisdB.set('foo', 'bar')
        my_logger.info("RedisSet " + str(time.time()))

        value = redisdB.get('foo')
        my_logger.info("RedisGet " + str(time.time()))
        if (value == 'bar'):
            my_logger.info("Connected to Redis dB")
        else:
            my_logger.error("Can not connect to Redis dB")
            raise Exception('Can not connect to Redis dB on port 6379')

        # drone reference data is in Redis database with a key for each drone
        # there is also a dockerHostsArray that contains a simplified view of the same data for performance
        # we will start/stop each docker container and also re-build the dockerHostsArray value
        rebuildDockerHostsArray()

        keys = redisdB.keys("connectionString:*")
        for key in keys:
            my_logger.debug("key = '" + key + "'")
            jsonObjStr = redisdB.get(key)
            my_logger.debug("redisDbObj = '" + jsonObjStr + "'")
            jsonObj = json.loads(jsonObjStr)
            connectionString = jsonObj['connectionString']
            vehicleName = jsonObj['name']
            vehicleType = jsonObj['vehicleType']
            dockerContainerId = jsonObj['dockerContainerId']
            droneId = key[17:]
            hostIp = connectionString[4:-6]
            port = connectionString[-5:]
            my_logger.info("connectionString:%s vehicleName:%s vehicleType:%s droneId:%s hostIp:%s port:%s ",
                           connectionString, vehicleName, vehicleType, droneId, hostIp, port)

            # stop and start this container (or start a new one if it doesn't exist)
            dockerClient = docker.DockerClient(version='1.27', base_url='tcp://' + hostIp + ':4243')  # docker.from_env(version='1.27')
            dockerAPIClient = docker.APIClient(version='1.27', base_url='tcp://' + hostIp + ':4243')  # docker.from_env(version='1.27')
            containerFound = False
            for container in dockerClient.containers.list(all=True):
                if (container.id == dockerContainerId):
                    containerFound = True
                    my_logger.info("Container %s found - restarting", container.id)
                    container.restart()
            if (containerFound == False):
                my_logger.info("Container not found - creating")

                # check if there is a container on this host already using this port
                containerWithPort = False
                for container in dockerClient.containers.list():

                    contPortObj = dockerAPIClient.port(container.id, 14550)
                    if (contPortObj is not None):
                        my_logger.info("Testing Container %s port %s", container.id, contPortObj)
                        if (contPortObj[0]['HostPort'] == port):
                            # container found. restart
                            my_logger.info("Container found - restarting")
                            containerWithPort = True
                            container.restart()
                            # update Redis with new container Id
                            dockerContainerId = container.id
                            redisdB.set(key,
                                        json.dumps({"connectionString": connectionString,
                                                    "name": vehicleName,
                                                    "vehicleType": vehicleType,
                                                    "startTime": time.time(),
                                                    "dockerContainerId": dockerContainerId}))

                if (containerWithPort == False):
                    my_logger.info("Container not found - creating new")

                    createDrone(vehicleType, vehicleName, '51.4049', '1.3049', '105', '0')

                    #dockerContainer = dockerClient.containers.run(dronesimImage, detach=True, ports={'14550/tcp': port}, name=droneId)
                    #dockerContainerId = dockerContainer.id
                    # update redis
                    # redisdB.set(key,
                    #            json.dumps({"connectionString": connectionString,
                    #                        "name": vehicleName,
                    #                        "vehicleType": vehicleType,
                    #                        "startTime": time.time(),
                    #                        "dockerContainerId": dockerContainerId}))

    except Exception as e:
        my_logger.warn("Caught exception: Unexpected error in validateAndRefreshContainers:")
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")

    return


def rebuildDockerHostsArray():
    # reset dockerHostsArray
    dockerHostsArray = [{"internalIP": defaultDockerHost, "usedPorts": []}]
    keys = redisdB.keys("connectionString:*")
    for key in keys:

        jsonObjStr = redisdB.get(key)
        jsonObj = json.loads(jsonObjStr)
        connectionString = jsonObj['connectionString']
        hostIp = connectionString[4:-6]
        port = connectionString[-5:]
        # check if this host already exists in dockerHostsArray
        found = False
        for host in dockerHostsArray:
            if (host['internalIP'] == hostIp):
                found = True
        if (found == False):
            dockerHostsArray.append({"internalIP": hostIp, "usedPorts": []})
        # add this drone to docker host
        for host in dockerHostsArray:
            if (host['internalIP'] == hostIp):
                host['usedPorts'].append(int(port))
    my_logger.info("dockerHostsArray (rebuilt)")
    my_logger.info(dockerHostsArray)
    redisdB.set("dockerHostsArray", json.dumps(dockerHostsArray))


def applyHeadders():
    my_logger.debug('Applying HTTP headers')
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
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
        my_logger.debug("connectVehicle called with inVehicleId = " + str(inVehicleId))
        # connectionString=connectionStringArray[inVehicleId]
        jsonObjStr = redisdB.get('connectionString:' + str(inVehicleId))
        my_logger.debug("Redis returns '" + str(jsonObjStr) + "'")
        if (jsonObjStr is None):
            my_logger.warn("Raising Vehicle not found warning")
            raise Warning('Vehicle not found ')
        my_logger.debug("redisDbObj = '" + jsonObjStr + "'")
        jsonObj = json.loads(jsonObjStr)
        connectionString = jsonObj['connectionString']
        vehicleName = jsonObj['name']
        vehicleType = jsonObj['vehicleType']
        vehicleStartTime = jsonObj['startTime']
        currentTime = time.time()
        timeSinceStart = currentTime - vehicleStartTime
        my_logger.debug("timeSinceStart= " + str(timeSinceStart))
        if (timeSinceStart < 10):  # less than 10 seconds so throw Exception
            my_logger.warn("Raising Vehicle starting up warning")
            raise Warning('Vehicle starting up ')

        my_logger.debug("connection string for vehicle " + str(inVehicleId) + "='" + connectionString + "'")
        # Connect to the Vehicle.
        if not connectionDict.get(inVehicleId):
            my_logger.info("connectionString: %s" % (connectionString,))
            my_logger.info("Connecting to vehicle on: %s" % (connectionString,))
            connectionNameTypeDict[inVehicleId] = {"name": vehicleName, "vehicleType": vehicleType}
            actionArrayDict[inVehicleId] = []  # create empty action array
            connectionDict[inVehicleId] = connect(connectionString, wait_ready=True, heartbeat_timeout=10)
            my_logger.info("actionArrayDict")
            my_logger.info(actionArrayDict)
        else:
            my_logger.debug("Already connected to vehicle")
    except Warning as w:
        my_logger.warn("Caught warning: " + str(w))
        raise Warning(str(w))
    except Exception as e:
        my_logger.warn("Caught exceptio: Unexpected error in connectVehicle:")
        my_logger.warn("VehicleId=" + str(inVehicleId))
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")
        raise Exception('Unexpected error connecting to vehicle ' + str(inVehicleId))
    return connectionDict[inVehicleId]


def latLonAltObj(inObj):
    output = {}
    output["lat"] = (inObj.lat)
    output["lon"] = (inObj.lon)
    output["alt"] = (inObj.alt)
    return output


def distanceInMeters(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat / 2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance * 1000


def getVehicleStatus(inVehicle, inVehicleId):
    # inVehicle is an instance of the Vehicle class
    outputObj = {}
    web.header('Content-Type', 'application/json')
    my_logger.debug("Autopilot Firmware version: %s" % inVehicle.version)
    outputObj["version"] = str(inVehicle.version)
    my_logger.debug("Global Location: %s" % inVehicle.location.global_frame)
    global_frame = latLonAltObj(inVehicle.location.global_frame)
    outputObj["global_frame"] = global_frame
    my_logger.debug("Global Location (relative altitude): %s" % inVehicle.location.global_relative_frame)
    global_relative_frame = latLonAltObj(inVehicle.location.global_relative_frame)
    outputObj["global_relative_frame"] = global_relative_frame
    my_logger.debug("Local Location: %s" % inVehicle.location.local_frame)  # NED
    local_frame = {}
    local_frame["north"] = (inVehicle.location.local_frame.north)
    local_frame["east"] = (inVehicle.location.local_frame.east)
    local_frame["down"] = (inVehicle.location.local_frame.down)
    outputObj["local_frame"] = local_frame
    my_logger.debug("Attitude: %s" % inVehicle.attitude)
    outputObj["attitude"] = {"pitch": inVehicle.attitude.pitch, "roll": inVehicle.attitude.roll, "yaw": inVehicle.attitude.yaw}
    my_logger.debug("Velocity: %s" % inVehicle.velocity)
    outputObj["velocity"] = (inVehicle.velocity)
    my_logger.debug("GPS: %s" % inVehicle.gps_0)
    outputObj["gps_0"] = {
        "eph": (
            inVehicle.gps_0.eph), "epv": (
            inVehicle.gps_0.eph), "fix_type": (
                inVehicle.gps_0.fix_type), "satellites_visible": (
                    inVehicle.gps_0.satellites_visible)}
    my_logger.debug("Groundspeed: %s" % inVehicle.groundspeed)
    outputObj["groundspeed"] = (inVehicle.groundspeed)
    my_logger.debug("Airspeed: %s" % inVehicle.airspeed)
    outputObj["airspeed"] = (inVehicle.airspeed)
    my_logger.debug("Gimbal status: %s" % inVehicle.gimbal)
    outputObj["gimbal"] = {"pitch": inVehicle.gimbal.pitch, "roll": inVehicle.gimbal.roll, "yaw": inVehicle.gimbal.yaw}
    my_logger.debug("Battery: %s" % inVehicle.battery)
    outputObj["battery"] = {"voltage": inVehicle.battery.voltage, "current": inVehicle.battery.current, "level": inVehicle.battery.level}
    my_logger.debug("EKF OK?: %s" % inVehicle.ekf_ok)
    outputObj["ekf_ok"] = (inVehicle.ekf_ok)
    my_logger.debug("Last Heartbeat: %s" % inVehicle.last_heartbeat)
    outputObj["last_heartbeat"] = (inVehicle.last_heartbeat)
    my_logger.debug("Rangefinder: %s" % inVehicle.rangefinder)
    outputObj["rangefinder"] = {"distance": inVehicle.rangefinder.distance, "voltage": inVehicle.rangefinder.voltage}
    my_logger.debug("Heading: %s" % inVehicle.heading)
    outputObj["heading"] = (inVehicle.heading)
    my_logger.debug("Is Armable?: %s" % inVehicle.is_armable)
    outputObj["is_armable"] = (inVehicle.is_armable)
    my_logger.debug("System status: %s" % inVehicle.system_status.state)
    outputObj["system_status"] = str(inVehicle.system_status.state)
    my_logger.debug("Mode: %s" % inVehicle.mode.name)  # settable
    outputObj["mode"] = str(inVehicle.mode.name)
    my_logger.debug("Armed: %s" % inVehicle.armed)  # settable
    outputObj["armed"] = (inVehicle.armed)

    zone = authorizedZoneDict.get(inVehicleId, None)
    if (zone is not None):
        outputObj["zone"] = authorizedZoneDict.get(inVehicleId, None)
        # check if vehicle still in zone
        distance = distanceInMeters(
            outputObj["zone"]["shape"]["lat"],
            outputObj["zone"]["shape"]["lon"],
            outputObj["global_frame"]["lat"],
            outputObj["global_frame"]["lon"])
        if (distance > 500):
            droneAPIAction.rtl(inVehicle)

    return outputObj

# get the next image and port to launch dronesim docker image (create new image if necessary)


def getNexthostAndPort():
    firstFreePort = 0
    keys = redisdB.keys("dockerHostsArray")
    dockerHostsArray = json.loads(redisdB.get(keys[0]))
    my_logger.info("dockerHostsArray")
    my_logger.info(dockerHostsArray)

    # initially always use current image
    for i in range(14550, 14560):
        # find first unused port
        portList = dockerHostsArray[0]['usedPorts']  # [{"internalIP":"172.17.0.1","usedPorts":[]}]
        if not(i in portList):
            firstFreePort = i
            break
    dockerHostsArray[0]['usedPorts'].append(i)
    my_logger.info("First unassigned port:" + str(firstFreePort))

    redisdB.set("dockerHostsArray", json.dumps(dockerHostsArray))
    return {"image": dockerHostsArray[0]['internalIP'], "port": firstFreePort}


def createDrone(droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir):
    connection = None
    dockerContainerId = "N/A"
    uuidVal = uuid.uuid4()
    key = str(uuidVal)[:8]

    environmentString = 'LOCATION=' + str(drone_lat) + ',' + str(drone_lon) + ',' + str(drone_alt) + ',' + str(drone_dir)
    my_logger.info("Start location environement %s", environmentString)

    # build simulated drone or proxy via Docker
    # docker api available on host at
    # http://172.17.0.1:4243/containers/json

    #private_ip_address=this.launchCloudImage('ami-5be0f43f', 't2.micro', ['sg-fd0c8394'])
    #connection="tcp:" + str(createresponse[0].private_ip_address) + ":14550"
    hostAndPort = getNexthostAndPort()
    dockerClient = docker.DockerClient(
        version='1.27',
        base_url='tcp://' +
        hostAndPort['image'] +
        ':4243')  # docker.from_env(version='1.27')
    dockerContainer = None
    containerName = 'lesterthomas/droneproxy:1.0'
    if (droneType == "simulated"):
        containerName = 'lesterthomas/dronesim:1.8'
        dockerContainer = dockerClient.containers.run(
            containerName,
            environment=[environmentString],
            detach=True,
            ports={
                '14550/tcp': hostAndPort['port']},
            name=key)
    else:
        containerName = 'lesterthomas/droneproxy:1.0'
        dockerContainer = dockerClient.containers.run(
            containerName,
            detach=True,
            ports={
                '14550/tcp': hostAndPort['port'] + 10,
                '14551/tcp': hostAndPort['port'],
                '14552/tcp': hostAndPort['port'] + 20},
            name=key)

    dockerContainerId = dockerContainer.id
    my_logger.info("container Id=" + str(dockerContainerId))

    connection = "tcp:" + hostAndPort['image'] + ":" + str(hostAndPort['port'])

    my_logger.debug(connection)

    my_logger.info("adding connectionString to Redis db with key '" + "connectionString:" + str(key) + "'")
    droneDBDetails = {"connectionString": connection,
                      "name": vehicleName,
                      "vehicleType": droneType,
                      "host": hostAndPort['image'],
                      "port": hostAndPort['port'],
                      "startTime": time.time(),
                      "dockerContainerId": dockerContainerId}
    if (droneType == 'real'):
        droneDBDetails['droneConnectTo'] = hostAndPort['port'] + 10
        droneDBDetails['groundstationConnectTo'] = hostAndPort['port'] + 20

    redisdB.set("connectionString:" + key,
                json.dumps(droneDBDetails))

    outputObj = {}
    outputObj["connection"] = connection
    if (droneType == "real"):
        outputObj["droneConnectTo"] = "tcp:droneapi.ddns.net:" + str(hostAndPort['port'] + 10)
        outputObj["groundstationConnectTo"] = "tcp:droneapi.ddns.net:" + str(hostAndPort['port'] + 20)
    outputObj["id"] = key
    my_logger.info("Return: =" + json.dumps(outputObj))
    return outputObj
