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
import droneAPICommand


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

    # FOr the time being there is only 1 worker running at port 1236
    return "http://" + defaultDockerHost + ":1236"


def getWorkerURLforVehicle(vehicle_id):
    """Return the URL to the correct Worker container for a given vehicle id."""

    # FOr the time being there is only 1 worker running at port 1236
    return "http://" + defaultDockerHost + ":1236"


def applyHeadders():
    my_logger.debug('Applying HTTP headers')
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    web.header('Access-Control-Allow-Headers', 'Content-Type')
    return


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
