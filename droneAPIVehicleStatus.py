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

    def __init__(self):
        return

    def GET(self, vehicle_id):
        try:
            my_logger.debug("GET: vehicle_id=" + str(vehicle_id))
            droneAPIUtils.applyHeadders()
            outputObj = {}

            actions = [{"method": "DELETE", "href": droneAPIUtils.homeDomain + "/vehicle/" +
                        str(vehicle_id), "title": "Delete connection to vehicle " + str(vehicle_id)}]

            json_str = droneAPIUtils.redisdB.get('connection_string:' + str(vehicle_id))
            individual_vehicle = json.loads(json_str)

            individual_vehicle['id'] = vehicle_id
            individual_vehicle['_links'] = {}
            individual_vehicle['_links']["self"] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id),
                "title": "Get status for vehicle " + str(vehicle_id) + "."}
            individual_vehicle['_links']['homeLocation'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/homeLocation",
                "title": "Get the home location for this vehicle"}
            individual_vehicle['_links']['command'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                "title": "Get the actions  for this vehicle."}
            individual_vehicle['_links']['mission'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/mission",
                "title": "Get the current mission commands from the vehicle."}
            individual_vehicle['_links']['simulator'] = {
                "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/simulator",
                "title": "Get the current simulator parameters from the vehicle."}
            individual_vehicle["_actions"] = actions
            output = json.dumps(individual_vehicle)
            my_logger.debug("Return: %s" % str(individual_vehicle))

        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def DELETE(self, vehicle_id):
        try:
            my_logger.info("DELETE: vehicle_id=" + str(vehicle_id))

            # remove reference t dronekit object
            droneAPIUtils.connectionDict[vehicle_id] = None
            # delete docker container for this vehicle
            json_str = droneAPIUtils.redisdB.get('connection_string:' + str(vehicle_id))
            my_logger.debug("redisDbObj = '" + json_str + "'")
            json_obj = json.loads(json_str)
            connection_string = json_obj['vehicle_details']['connection_string']

            droneAPIUtils.redisdB.delete("connection_string:" + vehicle_id)
            droneAPIUtils.redisdB.delete("vehicle_commands:" + vehicle_id)
            droneAPIUtils.connectionDict.pop("connection_string:" + vehicle_id, None)
            dockerHostsArray = json.loads(droneAPIUtils.redisdB.get("dockerHostsArray"))

            ipAddress = connection_string[4:-6]
            connection_stringLength = len(connection_string)
            my_logger.debug("connection_stringLength=" + str(connection_stringLength))
            port = connection_string[connection_stringLength - 5:]
            index = -1

            droneAPIUtils.rebuildDockerHostsArray()

            docker_container_id = json_obj['host_details']['docker_container_id']
            my_logger.info("Deleting container")
            my_logger.info("dockerHost = '" + ipAddress + "'")
            my_logger.info("port = '" + str(port) + "'")
            my_logger.info("containerId = '" + docker_container_id + "'")
            dockerClient = docker.DockerClient(version='1.27', base_url='tcp://' + ipAddress + ':4243')  # docker.from_env(version='1.27')
            container = dockerClient.containers.get(docker_container_id)
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

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
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


def terminateCloudInstance(vehicle_id):
    json_str = droneAPIUtils.redisdB.get('connection_string:' + str(vehicle_id))
    my_logger.debug("redisDbObj = '" + json_str + "'")
    json_obj = json.loads(json_str)
    connection_string = json_obj['host_details']['connection_string']
    ipAddress = connection_string[4:-6]

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
        my_logger.error(vehicle_id)
        my_logger.error("Exception=")
        my_logger.error(inst)
        # ignore error and continue

    return
