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

    def __init__():
        return

    def GET(self):
        try:
            my_logger.debug("GET")
            droneAPIUtils.applyHeadders()
            outputObj = []

            # get the query parameters
            query_parameters = web.input()
            my_logger.debug("Query parameters %s", str(query_parameters))
            keys = droneAPIUtils.redisdB.keys("connection_string:*")
            for key in keys:
                my_logger.debug("key = '" + key + "'")
                json_str = droneAPIUtils.redisdB.get(key)
                my_logger.debug("redisDbObj = '" + json_str + "'")
                individual_vehicle = json.loads(json_str)
                vehicle_id = key[18:]
                individual_vehicle["_links"] = {
                    "self": {
                        "href": droneAPIUtils.homeDomain +
                        "/vehicle/" +
                        str(vehicle_id),
                        "title": "Get status for vehicle " +
                        str(vehicle_id)}}
                individual_vehicle["id"] = vehicle_id
                vehicle_started = ('vehicle_status' in individual_vehicle.keys())
                if vehicle_started:
                    if not(hasattr(query_parameters, 'status')):
                        # by default the Redis query will return extra details. delete unless status query parameter is passed
                        del individual_vehicle['vehicle_status']
                    outputObj.append(individual_vehicle)

            actions = '[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). For simulated vehicle you can also give the starting lat, lon, alt (of ground above sea level) and dir (initial direction the drone is pointing). The connection_string is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + \
                droneAPIUtils.homeDomain + '/vehicle",\n"fields":[{"name":"vehicle_type", "type":{"listOfValues":["simulated","real"]}}, {"name":"connection_string","type":"string"}, {"name":"name","type":"string"}, {"name":"lat","type":"float"}, {"name":"lon","type":"float"}, {"name":"alt","type":"float"}, {"name":"dir","type":"float"}] }]\n'
            self = {"self": {"title": "Return the collection of available vehicles.", "href": droneAPIUtils.homeDomain + "/vehicle"}}
            my_logger.debug("actions")
            my_logger.debug(actions)
            jsonResponse = '{"_embedded":{"vehicle":' + \
                json.dumps(outputObj) + '},"_actions":' + actions + ',"_links":' + json.dumps(self) + '}'
            my_logger.debug("Return: =" + jsonResponse)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})

        return jsonResponse

    def POST(self):
        try:
            my_logger.info("POST:")
            droneAPIUtils.applyHeadders()
            dataStr = web.data()
            my_logger.info(dataStr)
            data = json.loads(dataStr)
            droneType = data["vehicle_type"]
            vehicleName = data["name"]
            drone_lat = data.get('lat', '51.4049')
            drone_lon = data.get('lon', '-1.3049')
            drone_alt = data.get('alt', '105')
            drone_dir = data.get('dir', '0')

            outputObj = droneAPIUtils.createDrone(droneType, vehicleName, drone_lat, drone_lon, drone_alt, drone_dir)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return json.dumps(outputObj)

    def OPTIONS(self):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: ")
            droneAPIUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output


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
