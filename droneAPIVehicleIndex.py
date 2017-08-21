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

    def GET(self):
        try:
            my_logger.debug("GET")
            droneAPIUtils.applyHeadders()
            outputObj = []

            # get the query parameters
            queryParameters = web.input()
            my_logger.debug("Query parameters %s", str(queryParameters))
            keys = droneAPIUtils.redisdB.keys("connectionString:*")
            for key in keys:
                my_logger.debug("key = '" + key + "'")
                jsonObjStr = droneAPIUtils.redisdB.get(key)
                my_logger.debug("redisDbObj = '" + jsonObjStr + "'")
                jsonObj = json.loads(jsonObjStr)
                connectionString = jsonObj['connectionString']
                vehicleName = jsonObj['name']
                vehicleType = jsonObj['vehicleType']
                host = jsonObj.get('host', '')
                port = jsonObj.get('port', '')
                vehicleId = key[17:]
                droneDetails = {
                    "_links": {
                        "self": {
                            "href": droneAPIUtils.homeDomain +
                            "/vehicle/" +
                            str(vehicleId),
                            "title": "Get status for vehicle " +
                            str(vehicleId)}},
                    "id": str(vehicleId),
                        "name": vehicleName,
                        "host": host,
                        "port": port,
                        "vehicleType": vehicleType}
                if (vehicleType == 'real'):
                    droneDetails['droneConnectTo'] = jsonObj.get('droneConnectTo', '')
                    droneDetails['groundstationConnectTo'] = jsonObj.get('groundstationConnectTo', '')
                if (hasattr(queryParameters, 'details')):
                    # try to get extra details. Ignore if this fails
                    try:
                        droneObj = droneAPIUtils.connectVehicle(vehicleId)
                        droneDetails['vehicleStatus'] = droneAPIUtils.getVehicleStatus(droneObj, vehicleId)
                    except Warning:
                        my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up %s", str(vehicleId))
                    except Exception:
                        my_logger.warn("vehicleStatus:GET Cant connect to vehicle %s", str(vehicleId))
                        tracebackStr = traceback.format_exc()
                        traceLines = tracebackStr.split("\n")
                        my_logger.warn("Trace: %s", traceLines)

                outputObj.append(droneDetails)

            actions = '[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). For simulated vehicle you can also give the starting lat, lon, alt (of ground above sea level) and dir (initial direction the drone is pointing). The connectionString is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + \
                droneAPIUtils.homeDomain + '/vehicle",\n"fields":[{"name":"vehicleType", "type":{"listOfValues":["simulated","real"]}}, {"name":"connectionString","type":"string"}, {"name":"name","type":"string"}, {"name":"lat","type":"float"}, {"name":"lon","type":"float"}, {"name":"alt","type":"float"}, {"name":"dir","type":"float"}] }]\n'
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
            droneType = data["vehicleType"]
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
