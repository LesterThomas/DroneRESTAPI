"""This module provides the API endpoint for the collection of vehicles (drones). It also lets you create
a new simulated drone or a connection to a real drone."""

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command, mavutil, APIException

import web
import logging
import traceback
import json
import time
import math
import docker
import redis
import boto3
import droneAPIUtils


my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class vehicleIndex:

    def __init__(self):
        return

    def POST(self):
        try:
            my_logger.info("POST:")
            droneAPIUtils.applyHeadders()
            dataStr = web.data()
            my_logger.info(dataStr)
            data = json.loads(dataStr)
            user_id = data["user_id"]
            droneType = data["vehicle_type"]
            vehicleName = data["name"]
            drone_lat = data.get('lat', '51.4049')
            drone_lon = data.get('lon', '-1.3049')
            drone_alt = data.get('alt', '105')
            drone_dir = data.get('dir', '0')

            outputObj = droneAPIUtils.createDrone(droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir, user_id)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return json.dumps(outputObj)


def launchCloudImage(ImageId, InstanceType, SecurityGroupIds):
    # build simulted drone using aws
    # test how many non-terminated instances there are
    ec2client = boto3.client('ec2')
    response = ec2client.describe_instances()
    # print(response)
    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # This sample print will output entire Dictionary object
            # print(instance)
            # This will print will output the value of the Dictionary key 'InstanceId'
            if (instance["State"]["Name"] != "terminated"):
                instances.append(instance["InstanceId"])

    my_logger.debug("Non terminated instances=")
    my_logger.debug(len(instances))
    if (len(instances) > 20):
        outputObj = {}
        outputObj["status"] = "Error: can't launch more than " + str(20) + " cloud images"
        return json.dumps(outputObj)

    my_logger.info("Creating new AWS image")
    ec2resource = boto3.resource('ec2')
    createresponse = ec2resource.create_instances(
        ImageId=ImageId,
        MinCount=1,
        MaxCount=1,
        InstanceType=InstanceType,
        SecurityGroupIds=SecurityGroupIds)
    my_logger.info(createresponse[0].private_ip_address)
    return createresponse[0].private_ip_address
