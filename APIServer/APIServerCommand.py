"""This module manages the API endpoint to manage an individual vehicles commands."""

import web
import logging
import traceback
import json
import time
import math
import requests
import APIServerUtils

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class Command(object):
    """THis class handles the /vehicle/*/command URL for the drone API."""

    def __init__(self):
        return

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            APIServerUtils.applyHeadders()
            output_obj = {}
            output = json.dumps(output_obj)
            my_logger.info("Return: =" + output)

        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": trace_lines})
        return output

    def GET(self, vehicle_id):
        """This method handles the GET request. It returns the list of previous commands,
        as well as the commands that are available for the drones current state."""
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))

            user_id = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            json_str = APIServerUtils.redisdB.get("vehicle:" + user_id + ":" + str(vehicle_id))
            my_logger.info("individual_vehicle: %s", "vehicle:" + user_id + ":" + str(vehicle_id))
            individual_vehicle = json.loads(str(json_str))
            if not('vehicle_status' in individual_vehicle.keys()):  # if the vehicle is starting up there will be no vehicle_status
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})

            vehicle_status = individual_vehicle['vehicle_status']

            output_obj = {}
            output_obj["_links"] = {
                "self": {
                    "href": APIServerUtils.homeDomain +
                    "/vehicle/" +
                    str(vehicle_id) +
                    "/command",
                    "title": "Get the commands for this vehicle."}}
            available_commands = []
            # available when armed
            my_logger.info("global_relative_frame.alt=%s", vehicle_status["global_relative_frame"]["alt"])
            if vehicle_status["armed"] == False:
                available_commands.append({
                    "name": "Arm",
                    "title": "Arm drone.",
                    "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Arm"}]
                })
            elif vehicle_status["global_relative_frame"]["alt"] > 1:  # if at height of >1 m
                available_commands.append({"name": "Region-of-Interest",
                                           "title": "Set a Region of Interest : When the drone is flying, it will face the point  <lat>,<lon>,<alt> (defaults to the home location)",
                                           "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                                           "method": "POST",
                                           "fields": [{"name": "name",
                                                       "type": "string",
                                                       "value": "Region-of-Interest"},
                                                      {"name": "lat",
                                                       "type": "float",
                                                       "value": 51.3946},
                                                      {"name": "lon",
                                                       "type": "float",
                                                       "value": -1.299},
                                                      {"name": "alt",
                                                       "type": "float",
                                                       "value": 105}]})
                available_commands.append({
                    "name": "Land",
                    "title": "Land at current location",
                    "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Land"}]
                })
                available_commands.append({
                    "name": "Return-to-Launch",
                    "title": "Return to launch: Return to the home location and land.",
                    "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Return-to-Launch"}]
                })
                available_commands.append({
                    "name": "Start-Mission",
                    "title": "Begin the pre-defined mission.",
                    "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Start-Mission"}]
                })
                available_commands.append({"name": "Goto-Absolute",
                                           "title": "Go to the location at latitude <lat>, longitude <lon> and altitude <alt> (above sea level).",
                                           "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                                           "method": "POST",
                                           "fields": [{"name": "name",
                                                       "type": "string",
                                                       "value": "Goto-Absolute"},
                                                      {"name": "lat",
                                                       "type": "float",
                                                       "value": 51.3946},
                                                      {"name": "lon",
                                                       "type": "float",
                                                       "value": -1.299},
                                                      {"name": "alt",
                                                       "type": "float",
                                                       "value": 105}]})
                available_commands.append({"name": "Goto-Relative-Home",
                                           "title": "Go to the location <north> meters North, <east> meters East and <up> meters vertically from the home location.",
                                           "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                                           "method": "POST",
                                           "fields": [{"name": "name",
                                                       "type": "string",
                                                       "value": "Goto-Relative-Home"},
                                                      {"name": "north",
                                                       "type": "float",
                                                       "value": 0},
                                                      {"name": "east",
                                                       "type": "float",
                                                       "value": 0},
                                                      {"name": "up",
                                                       "type": "float",
                                                       "value": 15}]})
                available_commands.append({"name": "Goto-Relative-Current",
                                           "title": "Go to the location <north> meters North, <east> meters East and <up> meters vertically from the current location.",
                                           "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                                           "method": "POST",
                                           "fields": [{"name": "name",
                                                       "type": "string",
                                                       "value": "Goto-Relative-Current"},
                                                      {"name": "north",
                                                       "type": "float",
                                                       "value": 20},
                                                      {"name": "east",
                                                       "type": "float",
                                                       "value": 20},
                                                      {"name": "up",
                                                       "type": "float",
                                                       "value": 0}]})
            elif vehicle_status["armed"]:
                available_commands.append({
                    "name": "Takeoff",
                    "title": "Takeoff in GUIDED mode to height of <height> (default 20m).",
                    "href": APIServerUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/command",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Takeoff"}, {"name": "height", "type": "float", "value": 20}]
                })

            output_obj['_actions'] = available_commands
            my_logger.debug(output_obj)
            output_obj['commands'] = updateActionStatus(user_id, vehicle_status, vehicle_id)
            output = json.dumps(output_obj)
            my_logger.info("Return: =" + output)
        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": trace_lines})
        return output

    def POST(self, vehicle_id):
        """This method handles the POST requests to send a new command to the drone. In this stateless server, it simply forwards the HTTP POST to the correct worker."""
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))

            user_id = APIServerUtils.getUserAuthorization()
            APIServerUtils.applyHeadders()

            dataStr = web.data()

            my_logger.debug(
                "HTTP Proxy calling http post at %s with data %s",
                APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                "/vehicle/" +
                str(vehicle_id) +
                "/command",
                dataStr)
            data_obj = json.loads(dataStr)
            data_obj['user_id'] = user_id

            result = requests.post(APIServerUtils.getWorkerURLforVehicle(vehicle_id) +
                                   "/vehicle/" + str(vehicle_id) + "/command", data=json.dumps(data_obj))
            my_logger.debug("HTTP Proxy result status_code %s reason %s", result.status_code, result.reason)
            my_logger.debug("HTTP Proxy result text %s ", result.text)

        except APIServerUtils.AuthFailedException as ex:
            return json.dumps({"error": "Authorization failure",
                               "details": ex.message})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": trace_lines})

        return result.text


def updateActionStatus(user_id, vehicle_status, vehicle_id):
    """This function allows you to monitor the progress of the last command.
    It updates the command status until it is complete (or errors) or is superceeded."""
    my_logger.info("############# in updateActionStatus")

    my_logger.info("vehicle_id")
    my_logger.info(vehicle_id)
    my_logger.info("#############")

    #command_array = APIServerUtils.commandArrayDict[vehicle_id]

    json_str = APIServerUtils.redisdB.get('vehicle_commands:' + user_id + ":" + str(vehicle_id))
    my_logger.info('vehicle_commands from Redis')
    my_logger.info(json_str)
    command_array_obj = json.loads(str(json_str))
    command_array = command_array_obj['commands']
    my_logger.info("command_array")
    my_logger.info(command_array)

    my_logger.info(command_array)

    if len(command_array) > 0:
        latestAction = command_array[len(command_array) - 1]

        if latestAction['command']['status'] == "Error":
            latestAction['complete'] = False
            latestAction['completeStatus'] = 'Error'
            return
        my_logger.debug("Latest Action:" + latestAction['command']['name'])

        if latestAction['command']['name'] == 'Start-Mission':
            # cant monitor progress at the moment
            my_logger.info("Cant monitor progress for mission")
        else:
            my_logger.debug("Monitoring progress for command '" + latestAction['command']['name'] + "'")
            my_logger.info(vehicle_status)
            targetCoordinates = latestAction['command']['coordinate']  # array with lat,lon,alt
            vehicleCoordinates = vehicle_status['global_relative_frame']  # object with lat,lon,alt attributes
            # Return-to-launch uses global_frame (alt is absolute)

            if latestAction['command']['name'] == 'Return-to-Launch':
                vehicleCoordinates = vehicle_status['global_frame']  # object with lat,lon,alt attributes

            horizontalDistance = APIServerUtils.distanceInMeters(
                targetCoordinates[0], targetCoordinates[1], vehicleCoordinates['lat'], vehicleCoordinates['lon'])
            verticalDistance = abs(targetCoordinates[2] - vehicleCoordinates['alt'])
            latestAction['horizontalDistance'] = round(horizontalDistance, 2)
            latestAction['verticalDistance'] = round(verticalDistance, 2)
            if (horizontalDistance < 5) and (verticalDistance < 1):
                latestAction['complete'] = True
                latestAction['completeStatus'] = 'Complete'
            else:
                latestAction['completeStatus'] = 'In progress'
                latestAction['complete'] = False
            # region of interest is special case
            if (latestAction['command']['name'] == 'Region-of-Interest'):
                latestAction['complete'] = True
                latestAction['completeStatus'] = 'Complete'

    if len(command_array) > 1:  # check if previous commands completed or were interrupted
        previousAction = command_array[len(command_array) - 2]
        if (previousAction.get('complete', False) == False):
            if (previousAction.get('completeStatus', 'In progress') == "In progress"):
                previousAction['completeStatus'] = 'Interrupted'
                previousAction['complete'] = False

    APIServerUtils.redisdB.set('vehicle_commands:' + user_id + ":" + str(vehicle_id), json.dumps({"commands": command_array}))

    return command_array
