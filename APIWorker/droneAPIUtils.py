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
from redis.sentinel import Sentinel
import socket
import docker
import psutil
import yaml
from kubernetes import client, config

from threading import Thread
import droneAPICommand
from droneAPIRedis import RedisManager
import droneAPIRedis

def cleanUp():
    global webApp, workerHostname
    try:
        # clean-up worker record
        my_logger.info("Cleaning-up and exiting")
        redisdB.delete('worker:' + workerHostname)
        webApp.stop
    except Exception as ex:
        my_logger.exception("Exception in cleanUp")
        my_logger.exception(ex)
        my_logger.exception("-------------------------------------------------")

    sys.exit()

def initaliseLogger():
    global my_logger
    # Set logging framework
    my_logger = logging.getLogger("DroneAPIWorker." + str(__name__))
    my_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    my_logger.info("##################################################################################")
    my_logger.info("Starting DroneAPIWorker at %s", str(time.time()))
    my_logger.info("##################################################################################")
    my_logger.info("Logging level:" + str(logging.DEBUG))
    return


def initaliseGlobals():
    global homeDomain, dronesimImage, droneproxyImage, connectionDict, connectionNameTypeDict, authorizedZoneDict, workerURL, workerMaster,   workerHostname

    # Set environment variables
    homeDomain = getEnvironmentVariable('DRONEAPI_URL')
    dronesimImage = getEnvironmentVariable('DOCKER_DRONESIM_IMAGE')
    droneproxyImage = getEnvironmentVariable('DOCKER_DRONEPROXY_IMAGE')
    workerMaster = False
    workerHostname = socket.gethostname()
    workerURL = workerHostname+".droneapiworker:1236"

    # set global variables
    connectionDict = {}  # holds a dictionary of DroneKit connection objects
    connectionNameTypeDict = {}  # holds the additonal name, type and start_time for the conections
    authorizedZoneDict = {}  # holds zone authorizations for each drone

    return



def initiliseRedisDB():
    global redisdBManager, redisdB
    try:

        my_logger.info("initiliseRedisDB testing redis manager")
        try:
           redisdBManager
        except NameError:
            redisdBManager=RedisManager() #create redisDbManager if it is not already defined

        my_logger.info("redisdBManager %s",redisdBManager)

        default_service_parameters={"max_server_iterations":10000, "min_number_of_servers":1, "iteration_time":0.25, "max_worker_iterations":10000, "min_number_of_workers":1, "target_number_of_workers":1, "target_number_of_servers":1, "worker_port_range_start":8000 }

        sentinel = Sentinel([('redis-sentinel', 26379)], socket_timeout=0.1)
        redisdB = sentinel.master_for('mymaster', socket_timeout=0.1)

        my_logger.info("initiliseRedisDB connected to redis")
        my_logger.info("Checking for mandatory key service_parameters")
        service_parameters=redisdBManager.get("service_parameters",default_service_parameters)

    except Exception as ex:
        my_logger.exception("Exception in initiliseRedisDB")
        my_logger.exception(ex)
        my_logger.exception("-------------------------------------------------")
        raise redis.exceptions.ConnectionError("Redis error in initiliseRedisDB")
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




def connectVehicle(user_id, inVehicleId):
    #global connection_string_array
    global redisdBManager
    global connectionDict, connectionNameTypeDict
    try:
        my_logger.debug("connectVehicle called with inVehicleId = " + str(inVehicleId))
        # connection_string=connection_string_array[inVehicleId]
        json_obj = redisdBManager.get('vehicle:' + user_id + ":" + str(inVehicleId))
        if 'vehicle_details' not in json_obj:
            my_logger.warn("Raising Vehicle not found warning")
            raise Warning('Vehicle not found ')

        vehicle_details = json_obj['vehicle_details']
        host_details = json_obj['host_details']
        connection_string = vehicle_details['connection_string']
        vehicleName = vehicle_details['name']
        vehicle_type = vehicle_details['vehicle_type']
        vehicle_start_time = host_details['start_time']
        currentTime = time.time()
        timeSinceStart = currentTime - vehicle_start_time
        my_logger.debug("timeSinceStart= " + str(timeSinceStart))
        if (timeSinceStart < 12):  # less than 12 seconds so throw Exception
            my_logger.warn("Raising Vehicle starting up warning")
            raise Warning('Vehicle starting up ')

        my_logger.debug("connection string for vehicle " + str(inVehicleId) + "='" + connection_string + "'")

        if host_details['worker_url'] == 'Power-Off':
            my_logger.warn("Raising Drone is Powered-Off warning")
            raise Warning('Drone is Powered-Off')

        # Connect to the Vehicle.
        elif not connectionDict.get(inVehicleId):

            my_logger.info("Connecting to vehicle on: %s" ,connection_string)
            vehicle_connection=connect(connection_string) #, wait_ready=True, heartbeat_timeout=10)
            connectionNameTypeDict[inVehicleId] = {"name": vehicleName, "vehicle_type": vehicle_type}
            connectionDict[inVehicleId] = vehicle_connection
        else:
            my_logger.debug("Already connected to vehicle")
    except Warning as w:
        my_logger.warn("Caught warning: " + str(w))
        raise Warning(str(w))
    except Exception as ex:
        my_logger.exception("Exception in connectVehicle")
        my_logger.warn("VehicleId=" + str(inVehicleId))
        my_logger.exception(ex)
        my_logger.exception("-------------------------------------------------")
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




#kubernetes helper functions ***************************************************************************
def create_deployment_object(inName, inImage, inEnvironment):
    # Configureate Pod template container
    container = client.V1Container(
        name=inName,
        image=inImage,
        ports=[client.V1ContainerPort(container_port=14550, name=inName),client.V1ContainerPort(container_port=14551, name=inName+'-dr'),client.V1ContainerPort(container_port=14552, name=inName+'-mp')],
        env=inEnvironment)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": inName, "tier": "backend"}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=1,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=inName),
        spec=spec)

    my_logger.info("Deployment object created.")
    my_logger.info(deployment)
    return deployment


def create_deployment(api_instance, deployment, inName):
    # Create deployement
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace="default")
    my_logger.info("Deployment created. status='%s'" % str(api_response.status))


def update_deployment(api_instance, deployment, inName):
    # Update container image
    deployment.spec.template.spec.containers[0].image = "nginx:1.9.1"
    # Update the deployment
    api_response = api_instance.patch_namespaced_deployment(
        name=inName,
        namespace="default",
        body=deployment)
    my_logger.info("Deployment updated. status='%s'" % str(api_response.status))


def delete_deployment(api_instance, inName):
    # Delete deployment
    api_response = api_instance.delete_namespaced_deployment(
        name=inName,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    my_logger.info("Deployment deleted. status='%s'" % str(api_response.status))

#kubernetes helper functions END***************************************************************************



def createDrone(droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir, user_id, in_key=''):
    global workerURL, dronesimImage, droneproxyImage
    connection = None
    my_logger.info("************ Creating Drone %s : %s : %s : %s : %s : %s : %s : %s ***********",
                   droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir, user_id, in_key)

    key = ''
    if (in_key == ''):
        uuidVal = uuid.uuid4()
        key = "d"+str(uuidVal)[:7]
    else:
        key = in_key

    #build simulated container using kubernetes
    deploymentName=key
    if droneType=="real":
        containerImageName=droneproxyImage
    else:
        containerImageName = dronesimImage
    my_logger.info("Kubernetes deployment name %s | image name %s",deploymentName, containerImageName)
    config.load_incluster_config()
    extensions_v1beta1 = client.ExtensionsV1beta1Api()
    environmentObj=[{"name":"LOCATION","value": str(drone_lat) + ',' + str(drone_lon) + ',' + str(drone_alt) + ',' + str(drone_dir)}]

    deployment = create_deployment_object(deploymentName, containerImageName,environmentObj)
    create_deployment(extensions_v1beta1, deployment,deploymentName)

    if droneType!="real":

        #Create Service for api to connect to sim
        api_instance = client.CoreV1Api()
        namespace = 'default'
        manifest = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": deploymentName,
                "labels":{
                    "app": deploymentName,
                    "tier":"backend"
                }
            },
            "spec": {
                "selector": {
                    "app": deploymentName,
                    "tier": "backend"
                },
                "type": "NodePort",
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 14550,
                        "targetPort": 14550,
                        "name": deploymentName
                    }
                ]
            }
        }

        api_response = api_instance.create_namespaced_service(namespace, manifest, pretty=True)

        #Create  Services for external groundstation to connect to proxy
        manifest = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": "proxy"+str(deploymentName),
                "labels":{
                    "app": deploymentName,
                    "tier":"backend"
                }
            },
            "spec": {
                "selector": {
                    "app": deploymentName,
                    "tier": "backend"
                },
                "type": "NodePort",
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 14552,
                        "targetPort": 14552,
                        "name": deploymentName+'-mp'
                    }
                ]
            }
        }
        api_response = api_instance.create_namespaced_service(namespace, manifest, pretty=True)
        mpNodePort=api_response.spec.ports[0].node_port
        my_logger.info("MP External Port: %s", mpNodePort)
    if droneType=="real":
        #Create Service for api to connect to proxy
        api_instance = client.CoreV1Api()
        namespace = 'default'
        manifest = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": deploymentName,
                "labels":{
                    "app": deploymentName,
                    "tier":"backend"
                }
            },
            "spec": {
                "selector": {
                    "app": deploymentName,
                    "tier": "backend"
                },
                "type": "NodePort",
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 14550,
                        "targetPort": 14550,
                        "name": deploymentName
                    }
                ]
            }
        }
        api_response = api_instance.create_namespaced_service(namespace, manifest, pretty=True)

        #Create  Services for external drone and groundstation to connect to proxy
        manifest = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": "proxy"+str(deploymentName),
                "labels":{
                    "app": deploymentName,
                    "tier":"backend"
                }
            },
            "spec": {
                "selector": {
                    "app": deploymentName,
                    "tier": "backend"
                },
                "type": "NodePort",
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 14551,
                        "targetPort": 14551,
                        "name": deploymentName+'-dr'
                    },
                    {
                        "protocol": "TCP",
                        "port": 14552,
                        "targetPort": 14552,
                        "name": deploymentName+'-mp'
                    }
                ]
            }
        }
        api_response = api_instance.create_namespaced_service(namespace, manifest, pretty=True)
        nodePort=api_response.spec.ports[0].node_port
        my_logger.info("Drone External Port: %s", nodePort)
        mpNodePort=api_response.spec.ports[1].node_port
        my_logger.info("MP External Port: %s", mpNodePort)


    port=14550
    connection = "tcp:" + deploymentName + ":" + str(port)

    my_logger.debug("Connection %s",connection)
    my_logger.info("adding vehicle to Redis db with key 'vehicle:%s:%s'", str(user_id), str(key))

    droneDBDetails = {"vehicle_details": {"connection_string": connection,
                                          "name": vehicleName,
                                          "port": port,
                                          "vehicle_type": droneType,
                                          "groundstation_connect_to": mpNodePort
                                          },
                      "host_details": {"host": deploymentName,
                                       "start_time": time.time(),
                                       "worker_url": workerURL}}

    if (droneType == 'real'):
        droneDBDetails['vehicle_details']['drone_connect_to'] = nodePort

    redisdBManager.set("vehicle:" + str(user_id) + ":" + key, droneDBDetails)
    redisdBManager.set("vehicle_commands:" + str(user_id) + ":" + key, {"commands": []})

    outputObj = {}
    outputObj["connection"] = connection
    if (droneType == "real"):
        outputObj["drone_connect_to"] = "tcp:droneapi.ddns.net:" + str(nodePort)
        outputObj["groundstation_connect_to"] = "tcp:droneapi.ddns.net:" + str(port + 20)
    outputObj["id"] = key
    my_logger.info("Return: =" + json.dumps(outputObj))
    return outputObj


def deleteDrone(vehicle_id):
    my_logger.info("Deleting Kubernetes deployment name %s",vehicle_id)
    config.load_incluster_config()
    extensions_v1beta1 = client.ExtensionsV1beta1Api()
    delete_deployment(extensions_v1beta1, vehicle_id)

    api_instance = client.CoreV1Api()
    api_response = api_instance.delete_namespaced_service(
        name=vehicle_id,
        namespace="default",
        pretty=True)
    my_logger.info("Service deleted. status='%s'" % str(api_response.status))
    api_response = api_instance.delete_namespaced_service(
        name='proxy'+vehicle_id,
        namespace="default",
        pretty=True)
    my_logger.info("Proxy Service deleted. status='%s'" % str(api_response.status))

    return

def getWorkerDetails():
    global webApp, workerHostname, redisdB
    worker_record={}
    try:
        service_parameters = redisdBManager.get("service_parameters")
        iteration_time = service_parameters['iteration_time']
        keys = redisdB.keys("vehicle:*")
        worker_record=redisdBManager.get('worker:' + workerHostname)
        if 'last_heartbeat' in worker_record: #check if worker record still running
            current_time=round(time.time(), 1)
            time_since_heartbeat=current_time-worker_record['last_heartbeat']
            worker_record['time_since_heartbeat']=time_since_heartbeat
            if (time_since_heartbeat>(iteration_time*2)):
                worker_record['running']=False
            else:
                worker_record['running']=True
        else:
            worker_record['running']=False
    except Warning as warn:
        my_logger.info("Caught warning in getWorkerDetails:%s ", str(warn))
        worker_record['running']=True #assume worker is still running
    except Exception as ex:
        my_logger.exception("Exception in getWorkerDetails")
        my_logger.exception(ex)
        my_logger.exception("-------------------------------------------------")
        worker_record['running']=False

    return worker_record




class worker(Thread):
    """This class provides a background worker thread that polls all the drone objects and updates the Redis database.
    This allows the GET URL requests to be served in a stateless manner from the Redis database."""

    def run(self):
        global webApp, workerHostname
        try:
            worker_iterations = 1
            continue_iterating = True
            while continue_iterating:
                try:
                    worker_iterations = worker_iterations + 1
                    service_parameters = redisdBManager.get("service_parameters")
                    iteration_time = service_parameters['iteration_time']

                    start_time = time.time()
                    containers_being_managed = 0
                    keys = redisdB.keys("vehicle:*")
                    for key in keys:
                        my_logger.debug("key = '%s'", key)
                        vehicle = redisdBManager.get(key)
                        if 'vehicle_details' in vehicle:  # vehicle may have been deleted
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
                    redisdBManager.set('worker:' + workerHostname, worker_record)

                    if (worker_iterations % 10 == 0):  # perform check every 10 iterations
                        continue_iterating = self.checkIfWorkerFinished(containers_being_managed, worker_iterations)
                        if workerMaster:
                            self.performMasterActions()

                    if (elapsed_time < iteration_time):
                        time.sleep(iteration_time - elapsed_time)
                except Warning as warn:
                    my_logger.info("Caught warning in worker:%s ", str(warn))
                    time.sleep(5) #sleep for 5 seconds to allow Redis to failover
                except Exception as ex:
                    my_logger.exception("Exception in worker")
                    my_logger.exception(ex)
                    my_logger.exception("-------------------------------------------------")
                    continue_iterating=False



            cleanUp()


        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in worker.run  %s ", traceLines)
            my_logger.exception("Exception in worker (outer)")
            my_logger.exception(ex)
            my_logger.exception("-------------------------------------------------")
            my_logger.exception("")
        return




    def executeUpdate(self, user_id, vehicle_id, vehicle, key):
        try:
            vehicle_obj = connectVehicle(user_id, vehicle_id)
            vehicle_status = getVehicleStatus(vehicle_obj, vehicle_id)
            vehicle['vehicle_status'] = vehicle_status
            vehicle['host_details']['update_heartbeat'] = time.time()
            redisdBManager.set(key, vehicle)
        except Warning as warn:
            my_logger.info("Caught warning in worker.run connectVehicle:%s ", str(warn))
        except APIException as ex:
            # these can safely be ignored during vehicle startup
            my_logger.info("Caught exception: APIException in worker.run connectVehicle")
            my_logger.exception(ex)
        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in executeUpdate. %s ", traceLines)
            my_logger.exception(ex)
            my_logger.exception("-------------------------------------------------")
            my_logger.exception("")
        return

    def checkIfWorkerFinished(self, containers_being_managed, worker_iterations):
        service_parameters = redisdBManager.get("service_parameters")
        max_worker_iterations = service_parameters['max_worker_iterations']

        if ((worker_iterations > max_worker_iterations) and (containers_being_managed == 0)
                ):  # if this worker has been going a long time and it is not managing any containers then stop this loop
            return False
        return True

    def checkToTakeoverMaster(self):
        # query redis to see if any other containers are the master. If none then takeover.
        global workerMaster
        if not workerMaster:
            keys = redisdB.keys("worker:*")
            master_found = False
            for key in keys:
                worker = redisdBManager.get(key)
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
        # query redis to see if any other containers are the master. If none then takeover.
        my_logger.info("Performing Master actions")


        return




