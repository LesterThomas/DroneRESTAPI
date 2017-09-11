"""This module has utility functions used by all the other modules in this App"""
# Import DroneKit-Python
from dronekit import connect, APIException

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
from threading import Thread
import APIServerCommand


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
    global homeDomain, defaultDockerHost

    # Set environment variables
    homeDomain = getEnvironmentVariable('DRONEAPI_URL')
    defaultDockerHost = getEnvironmentVariable('DOCKER_HOST_IP')
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
    my_logger.debug('Applying HTTP headers')
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    web.header('Access-Control-Allow-Headers', 'Content-Type, API_KEY')
    return


class AuthFailedException(Exception):
    """This is a custom exception class raised when the the user is not authorized"""
    pass


def getUserAuthorization():
    # my_logger.debug('getUserAuthorization')
    # my_logger.debug("web.ctx.env:%s",str(web.ctx.env))

    api_key = web.ctx.env.get('HTTP_API_KEY')
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
