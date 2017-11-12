"This module has utility functions used by all the other modules in this App"""
# Import DroneKit-Python
from dronekit import connect, APIException

import sys
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
import socket
import docker
import psutil
from threading import Thread
import droneAPICommand


def initaliseLogger():
    global my_logger

    # Set logging framework
    main_logger = logging.getLogger("DroneAPIServer")
    LOG_FILENAME = 'droneapi.log'
    main_logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000000, backupCount=5)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    main_logger.addHandler(handler)
    main_logger.propegate = False

    try:
        main_logger.addHandler(watchtower.CloudWatchLogHandler(send_interval=10))
    except BaseException:
        main_logger.warn("Can not add CloudWatch Log Handler")

    my_logger = logging.getLogger("DroneAPIServer." + str(__name__))

    my_logger.info("##################################################################################")
    my_logger.info("Starting DroneAPI at %s", str(time.time()))
    my_logger.info("##################################################################################")
    my_logger.info("Logging level:" + str(logging.INFO))

    return


def initaliseGlobals():
    global homeDomain, dronesimImage, defaultDockerHost, connectionDict, connectionNameTypeDict, authorizedZoneDict, workerURL, workerMaster, workerImage, serverImage, workerHostname

    # Set environment variables
    homeDomain = getEnvironmentVariable('DRONEAPI_URL')
    dronesimImage = getEnvironmentVariable('DOCKER_DRONESIM_IMAGE')
    workerImage = getEnvironmentVariable('DOCKER_WORKER_IMAGE')
    serverImage = getEnvironmentVariable('DOCKER_SERVER_IMAGE')
    defaultDockerHost = getEnvironmentVariable('DOCKER_HOST_IP')
    workerURL = getEnvironmentVariable('WORKER_URL')
    workerMaster = False
    workerHostname = socket.gethostname()

    # set global variables
    connectionDict = {}  # holds a dictionary of DroneKit connection objects
    connectionNameTypeDict = {}  # holds the additonal name, type and start_time for the conections
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
        # we will start/stop each docker container

        keys = redisdB.keys("vehicle:*")
        for key in keys:
            my_logger.debug("key = '" + key + "'")
            json_str = redisdB.get(key)
            my_logger.debug("redisDbObj = '" + json_str + "'")
            json_obj = json.loads(json_str)

            worker_url = json_obj['host_details']['worker_url']
            if worker_url == workerURL:  # if this vehicle is managed by this worker component then process

                vehicle_details = json_obj['vehicle_details']
                host_details = json_obj['host_details']
                connection_string = vehicle_details['connection_string']
                vehicleName = vehicle_details['name']
                vehicle_type = vehicle_details['vehicle_type']
                docker_container_id = host_details['docker_container_id']
                droneId = key[-8:]
                user_id = key[8:-9]
                hostIp = connection_string[4:-6]
                port = connection_string[-5:]
                my_logger.info("connection_string:%s vehicleName:%s vehicle_type:%s droneId:%s hostIp:%s port:%s user_id:%s ",
                               connection_string, vehicleName, vehicle_type, droneId, hostIp, port, user_id)

                # stop and start this container (or start a new one if it doesn't exist)
                dockerClient = docker.DockerClient(version='1.27', base_url='tcp://' + hostIp + ':4243')  # docker.from_env(version='1.27')
                dockerAPIClient = docker.APIClient(version='1.27', base_url='tcp://' + hostIp + ':4243')  # docker.from_env(version='1.27')
                containerFound = False
                for container in dockerClient.containers.list(all=True):
                    if (container.id == docker_container_id):
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
                                docker_container_id = container.id
                                redisdB.set(key,
                                            json.dumps({"vehicle_details": {"connection_string": connection_string,
                                                                            "name": vehicleName,
                                                                            "vehicle_type": vehicle_type,
                                                                            "start_time": time.time(),
                                                                            "docker_container_id": docker_container_id}}))

                    if (containerWithPort == False):
                        my_logger.info("Container not found - creating new")

                        createDrone(vehicle_type, vehicleName, '51.4049', '1.3049', '105', '0', user_id)

                        #dockerContainer = dockerClient.containers.run(dronesimImage, detach=True, ports={'14550/tcp': port}, name=droneId)
                        #docker_container_id = dockerContainer.id
                        # update redis
                        # redisdB.set(key,
                        #            json.dumps({"connection_string": connection_string,
                        #                        "name": vehicleName,
                        #                        "vehicle_type": vehicle_type,
                        #                        "start_time": time.time(),
                        #                        "docker_container_id": docker_container_id}))

    except Exception as e:
        my_logger.warn("Caught exception: Unexpected error in validateAndRefreshContainers:")
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")

    return


def startBackgroundWorker():
    worker().start()
    return


def applyHeadders():
    my_logger.debug('Applying HTTP headers')
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    web.header('Access-Control-Allow-Headers', 'Content-Type')
    return


def rebuildDockerHostsArray():
    # reset dockerHostsArray
    dockerHostsArray = [{"internalIP": defaultDockerHost, "usedPorts": []}]
    keys = redisdB.keys("connection_string:*")
    for key in keys:

        json_str = redisdB.get(key)
        json_obj = json.loads(json_str)
        vehicle_details = json_obj['vehicle_details']
        connection_string = vehicle_details['connection_string']
        hostIp = connection_string[4:-6]
        port = connection_string[-5:]
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
    return


def connectVehicle(user_id, inVehicleId):
    #global connection_string_array
    global redisdB
    global connectionDict
    try:
        my_logger.debug("connectVehicle called with inVehicleId = " + str(inVehicleId))
        # connection_string=connection_string_array[inVehicleId]
        json_str = redisdB.get('vehicle:' + user_id + ":" + str(inVehicleId))
        my_logger.debug("Redis returns '" + str(json_str) + "'")
        if (json_str is None):
            my_logger.warn("Raising Vehicle not found warning")
            raise Warning('Vehicle not found ')
        my_logger.debug("redisDbObj = '" + json_str + "'")
        json_obj = json.loads(json_str)
        vehicle_details = json_obj['vehicle_details']
        host_details = json_obj['host_details']
        connection_string = vehicle_details['connection_string']
        vehicleName = vehicle_details['name']
        vehicle_type = vehicle_details['vehicle_type']
        vehicle_start_time = host_details['start_time']
        currentTime = time.time()
        timeSinceStart = currentTime - vehicle_start_time
        my_logger.debug("timeSinceStart= " + str(timeSinceStart))
        if (timeSinceStart < 12):  # less than 10 seconds so throw Exception
            my_logger.warn("Raising Vehicle starting up warning")
            raise Warning('Vehicle starting up ')

        my_logger.debug("connection string for vehicle " + str(inVehicleId) + "='" + connection_string + "'")

        if host_details['worker_url'] == 'Power-Off':
            my_logger.warn("Raising Drone is Powered-Off warning")
            raise Warning('Drone is Powered-Off')

        # Connect to the Vehicle.
        elif not connectionDict.get(inVehicleId):
            my_logger.info("connection_string: %s" % (connection_string,))
            my_logger.info("Connecting to vehicle on: %s" % (connection_string,))
            connectionNameTypeDict[inVehicleId] = {"name": vehicleName, "vehicle_type": vehicle_type}
            connectionDict[inVehicleId] = connect(connection_string, wait_ready=True, heartbeat_timeout=10)
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
    my_logger.debug("Autopilot Firmware version: %s", inVehicle.version)
    outputObj["version"] = str(inVehicle.version)
    my_logger.debug("Global Location: %s", inVehicle.location.global_frame)
    global_frame = latLonAltObj(inVehicle.location.global_frame)
    outputObj["global_frame"] = global_frame
    my_logger.debug("Global Location (relative altitude): %s", inVehicle.location.global_relative_frame)
    global_relative_frame = latLonAltObj(inVehicle.location.global_relative_frame)
    outputObj["global_relative_frame"] = global_relative_frame
    my_logger.debug("Local Location: %s", inVehicle.location.local_frame)  # NED
    local_frame = {}
    local_frame["north"] = (inVehicle.location.local_frame.north)
    local_frame["east"] = (inVehicle.location.local_frame.east)
    local_frame["down"] = (inVehicle.location.local_frame.down)
    outputObj["local_frame"] = local_frame
    my_logger.debug("Attitude: %s", inVehicle.attitude)
    outputObj["attitude"] = {"pitch": inVehicle.attitude.pitch, "roll": inVehicle.attitude.roll, "yaw": inVehicle.attitude.yaw}
    my_logger.debug("Velocity: %s", inVehicle.velocity)
    outputObj["velocity"] = (inVehicle.velocity)
    my_logger.debug("GPS: %s", inVehicle.gps_0)
    outputObj["gps_0"] = {
        "eph": (
            inVehicle.gps_0.eph), "epv": (
            inVehicle.gps_0.eph), "fix_type": (
                inVehicle.gps_0.fix_type), "satellites_visible": (
                    inVehicle.gps_0.satellites_visible)}
    my_logger.debug("Groundspeed: %s", inVehicle.groundspeed)
    outputObj["groundspeed"] = (inVehicle.groundspeed)
    my_logger.debug("Airspeed: %s", inVehicle.airspeed)
    outputObj["airspeed"] = (inVehicle.airspeed)
    my_logger.debug("Gimbal status: %s", inVehicle.gimbal)
    outputObj["gimbal"] = {"pitch": inVehicle.gimbal.pitch, "roll": inVehicle.gimbal.roll, "yaw": inVehicle.gimbal.yaw}
    my_logger.debug("Battery: %s", inVehicle.battery)
    outputObj["battery"] = {"voltage": inVehicle.battery.voltage, "current": inVehicle.battery.current, "level": inVehicle.battery.level}
    my_logger.debug("EKF OK?: %s", inVehicle.ekf_ok)
    outputObj["ekf_ok"] = (inVehicle.ekf_ok)
    my_logger.debug("Last Heartbeat: %s", inVehicle.last_heartbeat)
    outputObj["last_heartbeat"] = (inVehicle.last_heartbeat)
    my_logger.debug("Rangefinder: %s", inVehicle.rangefinder)
    outputObj["rangefinder"] = {"distance": inVehicle.rangefinder.distance, "voltage": inVehicle.rangefinder.voltage}
    my_logger.debug("Heading: %s", inVehicle.heading)
    outputObj["heading"] = (inVehicle.heading)
    my_logger.debug("Is Armable?: %s", inVehicle.is_armable)
    outputObj["is_armable"] = (inVehicle.is_armable)
    my_logger.debug("System status: %s", inVehicle.system_status.state)
    outputObj["system_status"] = str(inVehicle.system_status.state)
    my_logger.debug("Mode: %s", inVehicle.mode.name)  # settable
    outputObj["mode"] = str(inVehicle.mode.name)
    my_logger.debug("Armed: %s", inVehicle.armed)  # settable
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
            droneAPICommand.rtl(inVehicle)
    my_logger.debug("Vehicle status output: %s" % outputObj)

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


def createDrone(droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir, user_id, in_key=''):
    global workerURL
    connection = None
    docker_container_id = "N/A"
    my_logger.info("************ Creating Drone %s : %s : %s : %s : %s : %s : %s : %s ***********",
                   droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir, user_id, in_key)

    key = ''

    if (in_key == ''):
        uuidVal = uuid.uuid4()
        key = str(uuidVal)[:8]
    else:
        key = in_key

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

    docker_container_id = dockerContainer.id
    my_logger.info("container Id=%s", str(docker_container_id))

    connection = "tcp:" + hostAndPort['image'] + ":" + str(hostAndPort['port'])

    my_logger.debug(connection)

    my_logger.info("adding vehicle to Redis db with key 'vehicle:%s:%s'", str(user_id), str(key))
    droneDBDetails = {"vehicle_details": {"connection_string": connection,
                                          "name": vehicleName,
                                          "port": hostAndPort['port'],
                                          "vehicle_type": droneType},
                      "host_details": {"host": hostAndPort['image'],
                                       "start_time": time.time(),
                                       "docker_container_id": docker_container_id,
                                       "worker_url": workerURL}}

    if (droneType == 'real'):
        droneDBDetails['vehicle_details']['drone_connect_to'] = hostAndPort['port'] + 10
        droneDBDetails['vehicle_details']['groundstation_connect_to'] = hostAndPort['port'] + 20

    redisdB.set("vehicle:" + str(user_id) + ":" + key, json.dumps(droneDBDetails))
    redisdB.set("vehicle_commands:" + str(user_id) + ":" + key, json.dumps({"commands": []}))

    outputObj = {}
    outputObj["connection"] = connection
    if (droneType == "real"):
        outputObj["drone_connect_to"] = "tcp:droneapi.ddns.net:" + str(hostAndPort['port'] + 10)
        outputObj["groundstation_connect_to"] = "tcp:droneapi.ddns.net:" + str(hostAndPort['port'] + 20)
    outputObj["id"] = key
    my_logger.info("Return: =" + json.dumps(outputObj))
    return outputObj


class worker(Thread):
    """This class provides a background worker thread that polls all the drone objects and updates the Redis database.
    This allows the GET URL requests to be served in a stateless manner from the Redis database."""

    def run(self):
        global webApp, workerHostname
        try:
            worker_iterations = 1
            continue_iterating = True
            while continue_iterating:
                worker_iterations = worker_iterations + 1
                service_parameters = json.loads(redisdB.get("service_parameters"))
                iteration_time = service_parameters['iteration_time']

                start_time = time.time()
                containers_being_managed = 0
                keys = redisdB.keys("vehicle:*")
                for key in keys:
                    my_logger.debug("key = '%s'", key)
                    json_str = redisdB.get(key)
                    if json_str is not None:  # vehicle may have been deleted
                        my_logger.debug("redisDbObj = '%s'", json_str)
                        vehicle = json.loads(json_str)
                        worker_url = vehicle['host_details']['worker_url']
                        if worker_url == workerURL:  # if this vehicle is managed by this worker component then process
                            containers_being_managed = containers_being_managed + 1
                            vehicle_id = key[-8:]
                            user_id = key[8:-9]
                            my_logger.info("Execute update for vehicle_id: %s ", vehicle_id)
                            my_logger.debug("user_id: %s", user_id)
                            self.executeUpdate(user_id, vehicle_id, vehicle, key)

                elapsed_time = time.time() - start_time
                my_logger.info("Background processing %i took %f", worker_iterations, elapsed_time)

                if (worker_iterations % 10 == 0):  # perform check every 100 iterations
                    self.checkToTakeoverMaster()

                process = psutil.Process(os.getpid())

                worker_record = {
                    'master': workerMaster,
                    'worker_url': workerURL,
                    'containers_being_managed': containers_being_managed,
                    'elapsed_time': elapsed_time,
                    'worker_iterations': worker_iterations,
                    'last_heartbeat': round(time.time(), 1),
                    'memory': process.memory_info().rss,
                    'cpu': psutil.cpu_percent(interval=0)}
                redisdB.set('worker:' + workerHostname, json.dumps(worker_record))

                if (worker_iterations % 10 == 0):  # perform check every 10 iterations
                    continue_iterating = self.checkIfWorkerFinished(containers_being_managed, worker_iterations)
                    if workerMaster:
                        self.performMasterActions()

                if (elapsed_time < iteration_time):
                    time.sleep(iteration_time - elapsed_time)

            # clean-up worker record
            my_logger.info("Cleaning-up and exiting")
            redisdB.delete('worker:' + workerHostname)
            webApp.stop()
            sys.exit()

        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in worker.run  %s ", traceLines)
            my_logger.exception(ex)
        return

    def executeUpdate(self, user_id, vehicle_id, vehicle, key):
        try:
            vehicle_obj = connectVehicle(user_id, vehicle_id)
            vehicle_status = getVehicleStatus(vehicle_obj, vehicle_id)
            vehicle['vehicle_status'] = vehicle_status
            vehicle['host_details']['update_heartbeat'] = time.time()
            redisdB.set(key, json.dumps(vehicle))
        except Warning as warn:
            my_logger.info("Caught warning in worker.run connectVehicle:%s ", str(warn))
        except APIException as ex:
            # these can safely be ignored during vehicle startup
            my_logger.info("Caught exception: APIException in worker.run connectVehicle")
            my_logger.exception(ex)
        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in worker.run connectVehicle. %s ", traceLines)
            my_logger.exception(ex)
        return

    def checkIfWorkerFinished(self, containers_being_managed, worker_iterations):
        service_parameters = json.loads(redisdB.get("service_parameters"))
        max_worker_iterations = service_parameters['max_worker_iterations']
        min_number_of_workers = service_parameters['min_number_of_workers']

        if ((worker_iterations > max_worker_iterations) and (containers_being_managed == 0)
                ):  # if this worker has been going a long time and it is not managing any containers then stop this loop
            keys = redisdB.keys("worker:*")
            if len(keys) > min_number_of_workers:
                return False
        return True

    def checkToTakeoverMaster(self):
        # query redis to see if any other containers are the master. If none then takeover.
        global workerMaster
        if not workerMaster:
            keys = redisdB.keys("worker:*")
            master_found = False
            for key in keys:
                worker = json.loads(redisdB.get(key))
                if worker['master']:
                    # test if still active
                    last_heartbeat = worker['last_heartbeat']
                    time_since_heartbeat = round(time.time() - last_heartbeat, 1)
                    if time_since_heartbeat < 10:
                        master_found = True
            if not master_found:
                workerMaster = True

        return

    def performMasterActions(self):
        global workerURL
        # query redis to see if any other containers are the master. If none then takeover.
        my_logger.info("Performing Master actions")

        service_parameters = json.loads(redisdB.get("service_parameters"))
        target_number_of_workers = service_parameters['target_number_of_workers']
        target_number_of_servers = service_parameters['target_number_of_servers']
        worker_port_range_start = service_parameters['worker_port_range_start']
        thisWorkerIP = workerURL[:-5]

        # *************************************************************
        # Check if I should create a new worker
        keys = redisdB.keys("worker:*")
        worker_urls_used = {}
        for key in keys:
            worker = json.loads(redisdB.get(key))
            my_logger.info(worker)
            # Check if any workers are unresponsive
            last_heartbeat = worker['last_heartbeat']
            time_since_heartbeat = round(time.time() - last_heartbeat, 1)
            my_logger.info("time_since_heartbeat:%f", time_since_heartbeat)
            if time_since_heartbeat > 10:
                redisdB.delete(key)
            else:
                worker_urls_used[worker['worker_url']] = True
                my_logger.info("Urls and Ports Used: %s", worker_urls_used)

        keys = redisdB.keys("worker:*")
        if len(keys) < target_number_of_workers:
            # start a new worker

            nextPortNumber = worker_port_range_start
            my_logger.info("thisWorkerIP: %s", thisWorkerIP)
            emptyPortFound = False

            while (emptyPortFound == False):
                test_key = thisWorkerIP + ":" + str(nextPortNumber)
                url_used = test_key in worker_urls_used
                my_logger.info("Testing if there is a worker at: %s returns %s", thisWorkerIP + ":" + str(nextPortNumber), str(url_used))
                if not url_used:
                    emptyPortFound = True
                else:
                    nextPortNumber = nextPortNumber + 1

            self.createWorker(thisWorkerIP, nextPortNumber)

        # *************************************************************
        # Check if I should create a new server
        keys = redisdB.keys("server:*")
        for key in keys:
            server = json.loads(redisdB.get(key))
            my_logger.info(server)
            # Check if any server are unresponsive
            last_heartbeat = server['last_heartbeat']
            time_since_heartbeat = round(time.time() - last_heartbeat, 1)
            my_logger.info("time_since_heartbeat:%f", time_since_heartbeat)
            if time_since_heartbeat > 10:
                redisdB.delete(key)

        keys = redisdB.keys("server:*")
        for key in keys:
            server = json.loads(redisdB.get(key))
            my_logger.info(server)

        if len(keys) < target_number_of_servers:
            # start a new server
            self.createServer()

        return

    def createWorker(self, worker_ip, worker_port):
        global defaultDockerHost, workerImage, serverImage, dronesimImage, homeDomain
        try:
            my_logger.info("Creating a new worker at: %s", "worker:" + worker_ip + ":" + str(worker_port))

            connection = None
            docker_container_id = "N/A"

            # build simulated drone or proxy via Docker
            # docker api available on host at
            # http://172.17.0.1:4243/containers/json
            dockerClient = docker.DockerClient(
                version='1.27',
                base_url='tcp://' +
                defaultDockerHost +
                ':4243')

            dockerClient.containers.prune(filters=None)  # remove any old containers to free-up the ports

            dockerContainer = None
            containerName = workerImage
            dockerContainer = dockerClient.containers.run(
                containerName,
                environment=[
                    "DRONEAPI_URL=" + homeDomain,
                    "DOCKER_DRONESIM_IMAGE=" + dronesimImage,
                    "DOCKER_WORKER_IMAGE=" + workerImage,
                    "DOCKER_SERVER_IMAGE=" + serverImage,
                    "DOCKER_HOST_IP=172.17.0.1",
                    "WORKER_URL=" + worker_ip + ":" + str(worker_port)],
                links={
                    "redis": "redis"},
                detach=True,
                ports={
                    '1234/tcp': worker_port})

            docker_container_id = dockerContainer.id
            my_logger.info("container Id=%s", str(docker_container_id))
        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in createWorker. %s ", traceLines)
            my_logger.exception(ex)
        return

    def createServer(self):

        global defaultDockerHost, serverImage, dronesimImage, homeDomain
        try:
            my_logger.info("Creating a new server")

            virtual_host_list = homeDomain.split("/")
            virtual_host = virtual_host_list[-1]
            my_logger.info("virtual_host: %s", virtual_host)

            connection = None
            docker_container_id = "N/A"

            # build simulated drone or proxy via Docker
            # docker api available on host at
            # http://172.17.0.1:4243/containers/json
            dockerClient = docker.DockerClient(
                version='1.27',
                base_url='tcp://' +
                defaultDockerHost +
                ':4243')

            dockerClient.containers.prune(filters=None)  # remove any old containers to free-up the ports

            dockerContainer = None
            containerName = serverImage

            dockerContainer = dockerClient.containers.run(
                containerName,
                environment=[
                    "DRONEAPI_URL=" + homeDomain,
                    "VIRTUAL_HOST=" + virtual_host,
                    "DOCKER_HOST_IP=172.17.0.1"],
                links={
                    "redis": "redis"},
                detach=True)

            docker_container_id = dockerContainer.id
            my_logger.info("container Id=%s", str(docker_container_id))
        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in createWorker. %s ", traceLines)
            my_logger.exception(ex)
        return
