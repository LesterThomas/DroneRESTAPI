"""Thi module manages the API endpoint for an individual vehicle (drone). It returns
the status for a drone and allows you to delete a drone"""


# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative, Command, mavutil, APIException

import web
import logging
import traceback
import json
import time
import math
import docker
import droneAPIUtils


my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class vehicleStatus:
    def GET(self, vehicleId):
        try:
            my_logger.debug("GET: vehicleId=" + str(vehicleId))
            droneAPIUtils.applyHeadders()
            outputObj = {}

            actions = [{"method": "DELETE", "href": droneAPIUtils.homeDomain + "/vehicle/" +
                        str(vehicleId), "title": "Delete connection to vehicle " + str(vehicleId)}]

            try:
                inVehicle = droneAPIUtils.connectVehicle(vehicleId)
            except Warning as w:
                my_logger.warn("Cant connect to vehicle: " + str(w) + " for vehicle with id " + str(vehicleId))
                return json.dumps({"error": "Cant connect to vehicle: " + str(w) +
                                   " for vehicle with id " + str(vehicleId), "_actions": actions})
            except Exception as e:
                my_logger.warn("Cant connect to vehicle:" + str(e) + " for vehicle with id " + str(vehicleId))
                jsonObjStr = droneAPIUtils.redisdB.get('connectionString:' + str(vehicleId))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicleId) +
                                   "with connection " + jsonObjStr, "_actions": actions})
            vehicleStatus = droneAPIUtils.getVehicleStatus(inVehicle, vehicleId)
            vehicleStatus["name"] = droneAPIUtils.connectionNameTypeDict[vehicleId]['name']
            vehicleStatus["vehicleType"] = droneAPIUtils.connectionNameTypeDict[vehicleId]['vehicleType']

            vehicleStatus['id'] = vehicleId
            vehicleStatus['_links'] = {}
            vehicleStatus['_links']["self"] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicleId),
                "title": "Get status for vehicle " + str(vehicleId) + "."}
            vehicleStatus['_links']['homeLocation'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicleId) + "/homeLocation",
                "title": "Get the home location for this vehicle"}
            vehicleStatus['_links']['action'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicleId) + "/action",
                "title": "Get the actions  for this vehicle."}
            vehicleStatus['_links']['mission'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicleId) + "/mission",
                "title": "Get the current mission commands from the vehicle."}
            vehicleStatus['_links']['simulator'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicleId) + "/simulator",
                "title": "Get the current simulator parameters from the vehicle."}
            output = ""
            outputObj = vehicleStatus
            outputObj["_actions"] = actions
            output = json.dumps(outputObj)
            my_logger.debug("Return: =" + output)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def DELETE(self, vehicleId):
        try:
            my_logger.info("DELETE: vehicleId=" + str(vehicleId))
            # delete docker container for this vehicle
            jsonObjStr = droneAPIUtils.redisdB.get('connectionString:' + str(vehicleId))
            my_logger.debug("redisDbObj = '" + jsonObjStr + "'")
            jsonObj = json.loads(jsonObjStr)
            connectionString = jsonObj['connectionString']

            droneAPIUtils.redisdB.delete("connectionString:" + vehicleId)
            droneAPIUtils.connectionDict.pop("connectionString:" + vehicleId, None)
            dockerHostsArray = json.loads(droneAPIUtils.redisdB.get("dockerHostsArray"))

            ipAddress = connectionString[4:-6]
            connectionStringLength = len(connectionString)
            my_logger.debug("connectionStringLength=" + str(connectionStringLength))
            port = connectionString[connectionStringLength - 5:]
            index = -1

            droneAPIUtils.rebuildDockerHostsArray()

            dockerContainerId = jsonObj['dockerContainerId']
            my_logger.info("Deleting container")
            my_logger.info("dockerHost = '" + ipAddress + "'")
            my_logger.info("port = '" + str(port) + "'")
            my_logger.info("containerId = '" + dockerContainerId + "'")
            dockerClient = docker.DockerClient(version='1.27', base_url='tcp://' + ipAddress + ':4243')  # docker.from_env(version='1.27')
            container = dockerClient.containers.get(dockerContainerId)
            container.stop()
            dockerClient.containers.prune(filters=None)

            outputObj = {"status": "success"}

            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def OPTIONS(self, vehicleId):
        try:
            my_logger.info("OPTIONS: vehicleId=" + str(vehicleId))
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


def terminateCloudInstance(vehicleId):
    jsonObjStr = droneAPIUtils.redisdB.get('connectionString:' + str(vehicleId))
    my_logger.debug("redisDbObj = '" + jsonObjStr + "'")
    jsonObj = json.loads(jsonObjStr)
    connectionString = jsonObj['connectionString']
    ipAddress = connectionString[4:-6]

    try:
        # terminate any AWS instances with that private IP address
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
                    if (instance.get("PrivateIpAddress", None) == ipAddress):
                        # my_logger.debug(instance)
                        my_logger.debug(
                            instance["PrivateIpAddress"],
                            instance["InstanceId"],
                            instance["InstanceType"],
                            instance["State"]["Name"])
                        instances.append(instance["InstanceId"])

        my_logger.debug("instances to terminate")
        my_logger.debug(instances)

        if (len(instances) > 0):
            # startresp=ec2client.start_instances(InstanceIds=["i-094270016448e61e2"])
            stopresp = ec2client.terminate_instances(InstanceIds=instances)
            my_logger.debug("Terminated instance")

    except Exception as inst:
        my_logger.error("Error conneting to AWS:")
        my_logger.error("VehicleId=")
        my_logger.error(vehicleId)
        my_logger.error("Exception=")
        my_logger.error(inst)
        # ignore error and continue

    return
