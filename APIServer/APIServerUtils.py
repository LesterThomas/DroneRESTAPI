"""This module has utility functions used by all the other modules in this App"""
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
import docker
import socket
import psutil
from threading import Thread
import APIServerCommand


def initaliseLogger():
    global my_logger

    # Set logging framework
    main_logger = logging.getLogger("DroneAPIServer")
    LOG_FILENAME = 'droneapi.log'
    main_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=2000000, backupCount=5)
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
    my_logger.info("Starting APIServer at  " + str(time.time()))
    my_logger.info("##################################################################################")
    my_logger.info("Logging level:" + str(logging.INFO))

    return


def rebuildDockerHostsArray():
    # reset dockerHostsArray
    dockerHostsArray = [{"internalIP": defaultDockerHost, "usedPorts": []}]
    keys = redisdB.keys("vehicle:*")
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


def initaliseGlobals():
    global homeDomain, defaultDockerHost, serverHostname, pagesServed

    # Set environment variables
    homeDomain = getEnvironmentVariable('DRONEAPI_URL')
    defaultDockerHost = getEnvironmentVariable('DOCKER_HOST_IP')
    serverHostname = socket.gethostname()
    pagesServed = 0
    my_logger.info("initaliseGlobals pagesServed: %i", pagesServed)
    return


def initiliseRedisDB():
    my_logger.info("initiliseRedisDB connecting to redis using host redis and port 6379")

    global redisdB
    redisdB = redis.Redis(host='redis', port=6379)  # redis or localhost
    my_logger.info("initiliseRedisDB connected to redis")

    my_logger.info("Getting all keys")

    keys = redisdB.keys("*")
    for key in keys:
        my_logger.info(key)

    my_logger.info("Finished getting all keys")


    my_logger.info("Finished getting all keys")
    my_logger.info("Checking for mandatory key service_parameters")

    service_parameters_str = redisdB.get("service_parameters")
    if service_parameters_str:
        my_logger.info("service_parameters found OK")
    else:
        service_parameters={"max_server_iterations":1000, "min_number_of_servers":1, "iteration_time":0.25, "max_worker_iterations":1000, "min_number_of_workers":1, "target_number_of_workers":1, "target_number_of_servers":1, "worker_port_range_start":8000 }
        service_parameters_str=json.dumps(service_parameters)
        redisdB.set("service_parameters",service_parameters_str)

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


def getNewWorkerURL():
    """Return the URL to a Worker container with capacity available to launch new vehicles."""
    keys = redisdB.keys("worker:*")
    min_number_managed = 1000
    worker_url = ''
    for key in keys:
        worker = json.loads(redisdB.get(key))

        containers_being_managed = worker['containers_being_managed']
        if containers_being_managed < min_number_managed:
            worker_url = worker['worker_url']
            min_number_managed = containers_being_managed

    # FOr the time being there is only 1 worker running at port 1236
    return "http://" + worker_url


def getWorkerURLforVehicle(user_id, vehicle_id):
    """Return the URL to the correct Worker container for a given vehicle id."""

    vehicle = json.loads(redisdB.get("vehicle:" + user_id + ":" + vehicle_id))
    worker_url = vehicle['host_details']['worker_url']
    return "http://" + worker_url


def getAllWorkerURLs():
    """Return the URLs to all Worker containers ."""

    # FOr the time being there is only 1 worker running at port 1236
    return ["http://" + defaultDockerHost + ":1236"]


def applyHeadders():
    global pagesServed
    my_logger.debug('Applying HTTP headers')
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    web.header('Access-Control-Allow-Headers', 'Content-Type, APIKEY')
    my_logger.info("applyHeadders pagesServed: %i", pagesServed)
    pagesServed = pagesServed + 1
    return


class AuthFailedException(Exception):
    """This is a custom exception class raised when the the user is not authorized"""
    pass


def getUserAuthorization():
    # my_logger.debug('getUserAuthorization')
    # my_logger.debug("web.ctx.env:%s",str(web.ctx.env))

    api_key = web.ctx.env.get('HTTP_APIKEY')
    if api_key is None:
        my_logger.warn("No api_key included in the HTTP header")
        my_logger.warn(web.ctx)
        raise AuthFailedException("No api_key included in the HTTP header")

    my_logger.info("api_key:%s", api_key)

    api_key_record = redisdB.get("api_key:" + api_key)
    if api_key_record:
        user_id = json.loads(api_key_record)['user']
        my_logger.info("user_id:%s", user_id)

    else:
        my_logger.warn("api_key %s is not valid", api_key)
        my_logger.warn(web.ctx)
        raise AuthFailedException("api_key is not valid")

    return user_id


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


class worker(Thread):
    """This class provides a background worker thread that polls all the drone objects and updates the Redis database.
    This allows the GET URL requests to be served in a stateless manner from the Redis database."""

    def run(self):
        global webApp, pagesServed, serverHostname

        try:
            worker_iterations = 1
            continue_iterating = True
            while continue_iterating:
                worker_iterations = worker_iterations + 1
                process = psutil.Process(os.getpid())

                server_record = {
                    'pages_served': pagesServed,
                    'worker_iterations': worker_iterations,
                    'last_heartbeat': round(time.time(), 1),
                    'memory': process.memory_info().rss,
                    'cpu': psutil.cpu_percent(interval=0)}

                redisdB.set('server:' + serverHostname, json.dumps(server_record))
                time.sleep(1)
                continue_iterating = self.checkIfServerFinished(worker_iterations)

        except Exception as ex:
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            my_logger.warn("Caught exception: Unexpected error in server.run  %s ", traceLines)
            my_logger.exception(ex)

        # clean-up worker record
        my_logger.info("Cleaning-up and exiting")
        redisdB.delete('server:' + serverHostname)
        webApp.stop()
        sys.exit()

        return

    def checkIfServerFinished(self, worker_iterations):
        service_parameters = json.loads(redisdB.get("service_parameters"))
        max_server_iterations = service_parameters['max_server_iterations']
        min_number_of_servers = service_parameters['min_number_of_servers']

        if worker_iterations > max_server_iterations:  # if this server has been going a long time
            keys = redisdB.keys("server:*")
            if len(keys) > min_number_of_servers:
                return False
        return True
