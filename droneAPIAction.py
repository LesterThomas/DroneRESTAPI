"""This module manages the API endpoint to manage an individual vehicles actions."""

# Import DroneKit-Python
from dronekit import VehicleMode, LocationGlobal, LocationGlobalRelative, mavutil

import web
import logging
import traceback
import json
import time
import math
import droneAPIUtils

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class Action(object):
    def OPTIONS(self, vehicle_id):
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            droneAPIUtils.applyHeadders()

            output_obj = {}
            output = json.dumps(output_obj)
            my_logger.info("Return: =" + output)

        except Exception as ex:
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": trace_lines})
        return output

    def GET(self, vehicle_id):
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))

            droneAPIUtils.applyHeadders()
            try:
                inVehicle = droneAPIUtils.connectVehicle(vehicle_id)
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicle_id)})

            vehicleStatus = droneAPIUtils.getVehicleStatus(inVehicle, vehicle_id)
            output_obj = {}
            output_obj["_links"] = {
                "self": {
                    "href": droneAPIUtils.homeDomain +
                    "/vehicle/" +
                    str(vehicle_id) +
                    "/action",
                    "title": "Get the actions for this vehicle."}}
            available_actions = []
            # available when armed
            my_logger.info("global_relative_frame.alt=%s", vehicleStatus["global_relative_frame"]["alt"])
            if (vehicleStatus["armed"] == False):
                available_actions.append({
                    "name": "Arm",
                    "title": "Arm drone.",
                    "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Arm"}]
                })
            elif (vehicleStatus["global_relative_frame"]["alt"] > 1):  # if at height of >1 m
                available_actions.append({"name": "Region-of-Interest",
                                          "title": "Set a Region of Interest : When the drone is flying, it will face the point  <lat>,<lon>,<alt> (defaults to the home location)",
                                          "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
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
                available_actions.append({
                    "name": "Land",
                    "title": "Land at current location",
                    "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Land"}]
                })
                available_actions.append({
                    "name": "Return-to-Launch",
                    "title": "Return to launch: Return to the home location and land.",
                    "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Return-to-Launch"}]
                })
                available_actions.append({
                    "name": "Start-Mission",
                    "title": "Begin the pre-defined mission.",
                    "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Start-Mission"}]
                })
                available_actions.append({"name": "Goto-Absolute",
                                          "title": "Go to the location at latitude <lat>, longitude <lon> and altitude <alt> (above sea level).",
                                          "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
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
                available_actions.append({"name": "Goto-Relative-Home",
                                          "title": "Go to the location <north> meters North, <east> meters East and <up> meters vertically from the home location.",
                                          "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                                          "method": "POST",
                                          "fields": [{"name": "name",
                                                      "type": "string",
                                                      "value": "Goto-Relative-Home"},
                                                     {"name": "north",
                                                      "type": "float",
                                                      "value": 30},
                                                     {"name": "east",
                                                      "type": "float",
                                                      "value": 30},
                                                     {"name": "up",
                                                      "type": "float",
                                                      "value": 10}]})
                available_actions.append({"name": "Goto-Relative-Current",
                                          "title": "Go to the location <north> meters North, <east> meters East and <up> meters vertically from the current location.",
                                          "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                                          "method": "POST",
                                          "fields": [{"name": "name",
                                                      "type": "string",
                                                      "value": "Goto-Relative-Current"},
                                                     {"name": "north",
                                                      "type": "float",
                                                      "value": 30},
                                                     {"name": "east",
                                                      "type": "float",
                                                      "value": 30},
                                                     {"name": "up",
                                                      "type": "float",
                                                      "value": 10}]})
            elif vehicleStatus["armed"]:
                available_actions.append({
                    "name": "Takeoff",
                    "title": "Takeoff in GUIDED mode to height of <height> (default 20m).",
                    "href": droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action",
                    "method": "POST",
                    "fields": [{"name": "name", "type": "string", "value": "Takeoff"}, {"name": "height", "type": "float", "value": 30}]
                })

            output_obj['_actions'] = available_actions
            my_logger.debug(output_obj)
            updateActionStatus(inVehicle, vehicle_id)
            output_obj['actions'] = droneAPIUtils.actionArrayDict[vehicle_id]
            output = json.dumps(output_obj)
            my_logger.info("Return: =" + output)
        except Exception as ex:
            my_logger.exception(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": trace_lines})
        return output

    def POST(self, vehicle_id):
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))
            try:
                inVehicle = droneAPIUtils.connectVehicle(vehicle_id)
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicle_id)})
            droneAPIUtils.applyHeadders()
            data = json.loads(web.data())
            # get latest data (inc home_location from vehicle)
            my_logger.debug("Getting commands:")

            cmds = inVehicle.commands
            my_logger.debug("Download:")

            cmds.download()
            my_logger.debug("Wait until ready:")
            cmds.wait_ready()

            my_logger.debug("Data:")
            my_logger.debug(data)
            value = data["name"]
            my_logger.debug("Value:")
            my_logger.debug(value)
            output_obj = {}
            if value == "Return-to-Launch":
                output_obj["action"] = rtl(inVehicle)
            elif value == "Arm":
                my_logger.debug("Armiong")
                output_obj["action"] = arm(inVehicle, vehicle_id)
            elif value == "Takeoff":
                height = data.get("height", 20)  # get height - default to 20
                my_logger.debug("Taking off to height of " + str(height))
                output_obj["action"] = takeoff(inVehicle, float(height))
            elif value == "Start-Mission":
                output_obj["action"] = auto(inVehicle)
            elif value == "Land":
                output_obj["action"] = land(inVehicle)
            elif value == "Goto-Absolute":
                default_location = inVehicle.location.global_frame  # default to current position
                my_logger.debug("Global Frame" + str(default_location))
                in_lat = data.get("lat", default_location.lat)
                in_lon = data.get("lon", default_location.lon)
                in_alt = data.get("alt", default_location.alt)
                location_obj = {'lat': float(in_lat), 'lon': float(in_lon), 'alt': float(in_alt)}
                output_obj["action"] = goto_absolute(inVehicle, location_obj)
            elif value == "Goto-Relative-Home":
                in_north = float(data.get("north", 0))
                in_east = float(data.get("east", 0))
                in_down = -float(data.get("up", 0))
                my_logger.debug("Goto-Relative-Home")
                my_logger.debug(in_north)
                my_logger.debug(in_east)
                my_logger.debug(in_down)
                output_obj["action"] = gotoRelative(inVehicle, in_north, in_east, in_down)
            elif value == "Goto-Relative-Current":
                in_north = float(data.get("north", 0))
                in_east = float(data.get("east", 0))
                in_down = -float(data.get("up", 0))
                output_obj["action"] = goto(inVehicle, in_north, in_east, in_down)
            elif value == "Region-of-Interest":
                cmds = inVehicle.commands
                cmds.download()
                cmds.wait_ready()
                default_location = inVehicle.home_location
                in_lat = data.get("lat", default_location.lat)
                in_lon = data.get("lon", default_location.lon)
                in_alt = data.get("alt", default_location.alt)
                location_obj = {'lat': float(in_lat), 'lon': float(in_lon), 'alt': float(in_alt)}
                output_obj["action"] = roi(inVehicle, location_obj)
            else:
                output_obj["action"] = {"status": "error", "name": value, "error": "No action found with name '" + value + "'."}
            action_array = droneAPIUtils.actionArrayDict[vehicle_id]
            if (len(action_array) == 0):
                output_obj['action']['id'] = 0
            else:
                output_obj['action']['id'] = action_array[len(action_array) - 1]['action']['id'] + 1
            action_array.append(output_obj)
            if (len(action_array) > 10):
                action_array.pop(0)
            output_obj['href'] = droneAPIUtils.homeDomain + "/vehicle/" + str(vehicle_id) + "/action"
            my_logger.info("Return: =" + json.dumps(output_obj))

        except Exception as e:
            my_logger.exception(e)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": trace_lines})

        return json.dumps(output_obj)


# methods to support the different actions
def rtl(inVehicle):

    output_obj = {}
    if inVehicle.armed:
        output_obj["name"] = "Return-to-Launch"
        output_obj["status"] = "success"
        # coodinates are same as home
        home_location = inVehicle.home_location
        output_obj["coordinate"] = [home_location.lat, home_location.lon, home_location.alt]
        output_obj["param1"] = 0
        output_obj["param2"] = 0
        output_obj["param3"] = 0
        output_obj["param4"] = 0
        output_obj["command"] = 20
        my_logger.info("Returning to Launch")
        inVehicle.mode = VehicleMode("RTL")
    else:
        output_obj["name"] = "Return-to-Launch"
        output_obj["status"] = "Error"
        output_obj["error"] = "Vehicle not armed"
        my_logger.warn("RTL error - Vehicle not armed")

    return output_obj


def arm(inVehicle, invehicle_id):
    output_obj = {}
    if inVehicle.is_armable:
        output_obj["name"] = "Arm"
        output_obj["status"] = "success"
        # coodinates are same as current + height
        currentLocation = inVehicle.location.global_relative_frame
        output_obj["coordinate"] = [currentLocation.lat, currentLocation.lon, 0]
        output_obj["param1"] = 1
        output_obj["param2"] = 0
        output_obj["param3"] = 0
        output_obj["param4"] = 0
        output_obj["command"] = 400
        my_logger.info("Arming motors")
        # Copter should arm in GUIDED mode
        inVehicle.mode = VehicleMode("GUIDED")
        inVehicle.armed = True

        output_obj["zone"] = {
            "shape": {
                "name": "circle",
                "lat": currentLocation.lat,
                "lon": currentLocation.lon,
                "radius": 500}}
        if (output_obj["zone"]["shape"]["lat"] != 0):  # only automatically assign a zone if it is not 0,0,0,0
            droneAPIUtils.authorizedZoneDict[invehicle_id] = output_obj["zone"]

        # Confirm vehicle armed before attempting to take off
        while not inVehicle.armed:
            my_logger.info(" Waiting for arming...")
            time.sleep(1)
    else:
        output_obj["name"] = "Arm"
        output_obj["status"] = "Error"
        output_obj["error"] = "vehicle not armable"
        my_logger.warn("vehicle not armable")
    return output_obj


def takeoff(inVehicle, inHeight):
    output_obj = {}
    if inVehicle.armed:
        output_obj["name"] = "Takeoff"
        output_obj["height"] = inHeight
        output_obj["status"] = "success"
        # coodinates are same as current + height
        currentLocation = inVehicle.location.global_relative_frame
        output_obj["coordinate"] = [currentLocation.lat, currentLocation.lon, inHeight]
        output_obj["param1"] = 0
        output_obj["param2"] = 0
        output_obj["param3"] = 0
        output_obj["param4"] = 0
        output_obj["command"] = 22
        inVehicle.mode = VehicleMode("GUIDED")
        my_logger.info("Taking off!")
        inVehicle.simple_takeoff(inHeight)  # Take off to target altitude
    else:
        output_obj["name"] = "Takeoff"
        output_obj["status"] = "Error"
        output_obj["error"] = "vehicle not armed"
        my_logger.warn("vehicle not armed")
    return output_obj


def auto(inVehicle):
    output_obj = {}
    if inVehicle.armed:
        output_obj["name"] = "Start-Mission"
        output_obj["status"] = "success"
        my_logger.info("Auto mission")
        if inVehicle.mode.name == "AUTO":
            # vehicle already in auto mode - swap it into GUIDED first.
            inVehicle.mode = VehicleMode("GUIDED")
            time.sleep(1)
        inVehicle.mode = VehicleMode("AUTO")
    else:
        output_obj["name"] = "Start-Mission"
        output_obj["status"] = "Error"
        output_obj["error"] = "Vehicle not armed"
    return output_obj


def land(inVehicle):
    output_obj = {}
    if inVehicle.armed:
        output_obj["name"] = "Land"
        output_obj["status"] = "success"
        # coodinates are same as current
        currentLocation = inVehicle.location.global_relative_frame
        output_obj["coordinate"] = [currentLocation.lat, currentLocation.lon, 0]
        output_obj["param1"] = 0
        output_obj["param2"] = 0
        output_obj["param3"] = 0
        output_obj["param4"] = 0
        output_obj["command"] = 23
        my_logger.info("Landing")
        inVehicle.mode = VehicleMode("LAND")
    else:
        output_obj["name"] = "Land"
        output_obj["status"] = "Error"
        output_obj["error"] = "Vehicle not armed"
    return output_obj


def goto(inVehicle, dNorth, dEast, dDown):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
    """
    output_obj = {}
    if inVehicle.armed:
        distance = round(math.sqrt(dNorth * dNorth + dEast * dEast))
        my_logger.info("Goto a distance of " + str(distance) + "m.")
        if distance > 1000:
            output_obj["status"] = "Error"
            output_obj["error"] = "Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            output_obj["name"] = "Max-Distance-Error"
        else:
            output_obj["name"] = "Goto-Relative-Current"
            output_obj["status"] = "success"
            inVehicle.mode = VehicleMode("GUIDED")
            currentLocation = inVehicle.location.global_relative_frame
            target_location = get_location_metres(currentLocation, dNorth, dEast)
            target_location.alt = target_location.alt - dDown
            # coodinates are target
            output_obj["coordinate"] = [target_location.lat, target_location.lon, target_location.alt]
            output_obj["param1"] = 0
            output_obj["param2"] = 0
            output_obj["param3"] = 0
            output_obj["param4"] = 0
            output_obj["command"] = 16
            inVehicle.simple_goto(target_location, groundspeed=10)
    else:
        output_obj["name"] = "Goto-Relative-Current"
        output_obj["status"] = "Error"
        output_obj["error"] = "Vehicle not armed"
    return output_obj


def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to
    the current vehicle position.
    """
    my_logger.debug("lat:" + str(original_location.lat) + " lon:" + str(original_location.lon))
    my_logger.debug("north:" + str(dNorth) + " east:" + str(dEast))

    earth_radius = 6378137.0  # Radius of "spherical" earth
    # Coordinate offsets in radians
    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * original_location.lat / 180))

    # New position in decimal degrees
    newlat = original_location.lat + (dLat * 180 / math.pi)
    newlon = original_location.lon + (dLon * 180 / math.pi)
    if isinstance(original_location, LocationGlobal):
        target_location = LocationGlobal(newlat, newlon, original_location.alt)
    elif isinstance(original_location, LocationGlobalRelative):
        target_location = LocationGlobalRelative(newlat, newlon, original_location.alt)
    else:
        raise Exception("Invalid Location object passed")
    return target_location


def gotoRelative(inVehicle, north, east, down):
    output_obj = {}
    if inVehicle.armed:
        output_obj["name"] = "Goto-Relative-Home"
        output_obj["status"] = "success"
        inVehicle.mode = VehicleMode("GUIDED")

        home_location = inVehicle.home_location

        #currentLocation = inVehicle.location.global_relative_frame
        target_location = get_location_metres(home_location, north, east)
        target_location.alt = home_location.alt - down
        distance = round(
            droneAPIUtils.distanceInMeters(
                target_location.lat,
                target_location.lon,
                inVehicle.location.global_frame.lat,
                inVehicle.location.global_frame.lon))
        if distance > 1000:
            output_obj["status"] = "Error"
            output_obj["error"] = "Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            output_obj["name"] = "Max-Distance-Error"
        else:
            # coodinates are target
            output_obj["coordinate"] = [target_location.lat, target_location.lon, -down]
            output_obj["param1"] = 0
            output_obj["param2"] = 0
            output_obj["param3"] = 0
            output_obj["param4"] = 0
            output_obj["command"] = 16
            inVehicle.simple_goto(target_location, groundspeed=10)
    else:
        output_obj["name"] = "Goto-Relative-Home"
        output_obj["status"] = "Error"
        output_obj["error"] = "Vehicle not armed"
    return output_obj


def goto_absolute(inVehicle, inLocation):
    output_obj = {}
    if inVehicle.armed:
        output_obj["name"] = "Goto-Absolute"
        output_obj["status"] = "success"
        my_logger.debug(" Goto Location: %s" % inLocation)
        output = {"global_frame": inLocation}
        my_logger.debug("lat" + str(inLocation['lat']))

        distance = round(
            droneAPIUtils.distanceInMeters(
                inLocation['lat'],
                inLocation['lon'],
                inVehicle.location.global_frame.lat,
                inVehicle.location.global_frame.lon))
        if distance > 1000:
            output_obj["status"] = "Error"
            output_obj["error"] = "Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            output_obj["name"] = "Max-Distance-Error"
        else:
            inVehicle.mode = VehicleMode("GUIDED")
            # coodinates are target
            output_obj["coordinate"] = [inLocation['lat'], inLocation['lon'], inLocation['alt']]
            output_obj["param1"] = 0
            output_obj["param2"] = 0
            output_obj["param3"] = 0
            output_obj["param4"] = 0
            output_obj["command"] = 16

            inVehicle.simple_goto(LocationGlobal(inLocation['lat'], inLocation['lon'], inLocation['alt']), groundspeed=10)
    else:
        output_obj["name"] = "Goto-Absolute"
        output_obj["status"] = "Error"
        output_obj["error"] = "Vehicle not armed"
    return output_obj


def roi(inVehicle, inLocation):
    output_obj = {}
    output_obj["name"] = "Region-of-Interest"
    output_obj["status"] = "success"
    my_logger.debug(" Home Location: %s" % inLocation)
    output = {"home_location": inLocation}
    my_logger.debug("lat" + str(inLocation['lat']))
    # coodinates are target
    output_obj["coordinate"] = [inLocation['lat'], inLocation['lon'], inLocation['alt']]
    output_obj["param1"] = 0
    output_obj["param2"] = 0
    output_obj["param3"] = 0
    output_obj["param4"] = 0
    output_obj["command"] = 80
    set_roi(inVehicle, inLocation)
    return output_obj


def set_roi(inVehicle, location):
    # create the MAV_CMD_DO_SET_ROI command
    msg = inVehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI,  # command
        0,  # confirmation
        0, 0, 0, 0,  # params 1-4
        location['lat'],
        location['lon'],
        location['alt']
    )
    # send command to vehicle
    inVehicle.send_mavlink(msg)


def updateActionStatus(inVehicle, invehicle_id):
    # test to see whether the vehicle is at the target location of the action
    my_logger.info("############# in updateActionStatus")

    my_logger.info("invehicle_id")
    my_logger.info(invehicle_id)
    my_logger.info("droneAPIUtils.actionArrayDict")
    my_logger.info(droneAPIUtils.actionArrayDict)
    my_logger.info("#############")

    action_array = droneAPIUtils.actionArrayDict[invehicle_id]

    my_logger.info(action_array)

    if (len(action_array) > 0):
        latestAction = action_array[len(action_array) - 1]

        if (latestAction['action']['status'] == "Error"):
            latestAction['complete'] = False
            latestAction['completeStatus'] = 'Error'
            return
        my_logger.debug("Latest Action:" + latestAction['action']['name'])

        if (latestAction['action']['name'] == 'Start-Mission'):
            # cant monitor progress at the moment
            my_logger.info("Cant monitor progress for mission")
        else:
            my_logger.debug("Monitoring progress for action '" + latestAction['action']['name'] + "'")

            targetCoordinates = latestAction['action']['coordinate']  # array with lat,lon,alt
            my_logger.info(inVehicle)
            vehicleCoordinates = inVehicle.location.global_relative_frame  # object with lat,lon,alt attributes
            # Return-to-launch uses global_frame (alt is absolute)

            if (latestAction['action']['name'] == 'Return-to-Launch'):
                vehicleCoordinates = inVehicle.location.global_frame  # object with lat,lon,alt attributes

            horizontalDistance = droneAPIUtils.distanceInMeters(
                targetCoordinates[0], targetCoordinates[1], vehicleCoordinates.lat, vehicleCoordinates.lon)
            verticalDistance = abs(targetCoordinates[2] - vehicleCoordinates.alt)
            latestAction['horizontalDistance'] = round(horizontalDistance, 2)
            latestAction['verticalDistance'] = round(verticalDistance, 2)
            if ((horizontalDistance < 5) and (verticalDistance < 1)):
                latestAction['complete'] = True
                latestAction['completeStatus'] = 'Complete'
            else:
                latestAction['completeStatus'] = 'In progress'
                latestAction['complete'] = False
            # region of interest is special case
            if (latestAction['action']['name'] == 'Region-of-Interest'):
                latestAction['complete'] = True
                latestAction['completeStatus'] = 'Complete'

    if (len(action_array) > 1):  # check if previous actions completed or were interrupted
        previousAction = action_array[len(action_array) - 2]
        if (previousAction.get('complete', False) == False):
            if (previousAction.get('completeStatus', 'In progress') == "In progress"):
                previousAction['completeStatus'] = 'Interrupted'
                previousAction['complete'] = False

    return
