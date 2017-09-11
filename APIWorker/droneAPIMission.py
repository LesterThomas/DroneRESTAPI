"""This module provides the API endpoint to manage the missions for a drone. A mission is a
series of actions that can be loaded to a drone and executed automatically"""

# Import DroneKit-Python
from dronekit import Command, mavutil

import web
import logging
import traceback
import json
import droneAPIUtils

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class mission:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))
            my_logger.debug("vehicle_id = '" + vehicle_id + "'")
            droneAPIUtils.applyHeadders()
            query_parameters = web.input()
            user_id = query_parameters['user_id']
            output = getMissionActions(user_id, vehicle_id)
            my_logger.info("Return: =" + output)
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output

    def POST(self, vehicle_id):
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))
            droneAPIUtils.applyHeadders()
            try:
                data = json.loads(web.data())
                user_id = data["user_id"]
                inVehicle = droneAPIUtils.connectVehicle(user_id, vehicle_id)
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
            except Exception:  # pylint: disable=W0703
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicle_id)})
            # download existing commands
            my_logger.info("download existing commands")
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            # clear the commands
            my_logger.info("clearing existing commands")
            cmds.clear()
            inVehicle.flush()
            missionActionArray = data['mission_items']
            my_logger.info("missionCommandArray:")
            my_logger.info(missionActionArray)
            # add new commands
            for missionAction in missionActionArray:
                my_logger.info(missionAction)
                lat = missionAction['coordinate'][0]
                lon = missionAction['coordinate'][1]
                altitude = missionAction['coordinate'][2]
                cmd = Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, missionAction['command'],
                              0, 0, missionAction['param1'], missionAction['param2'], missionAction['param3'], missionAction['param4'],
                              lat, lon, altitude)
                my_logger.info("Add new command with altitude:")
                my_logger.info(altitude)
                cmds.add(cmd)
            inVehicle.flush()
            my_logger.info("Command added")
            output = getMissionActions(user_id, vehicle_id)
            my_logger.info("Return: =" + output)
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            droneAPIUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output


def getMissionActions(user_id, vehicle_id):
    try:
        try:
            inVehicle = droneAPIUtils.connectVehicle(user_id, vehicle_id)
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicle_id))
            return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
        except Exception:  # pylint: disable=W0703
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicle_id))
            return json.dumps({"error": "Cant connect to vehicle " + str(vehicle_id)})
        droneAPIUtils.getVehicleStatus(inVehicle, vehicle_id)
        outputObj = {"_actions": [{"name": "upload mission", "method": "POST", "title": "Upload a new mission to the vehicle. The mission is a collection of mission actions with <command>, <coordinate[lat,lon,alt]> and command specific <param1>,<param2>,<param3>,<param4>. The command-set is described at https://pixhawk.ethz.ch/mavlink/",
                                   "fields": [{"name": "coordinate", "type": "array", "value": [51.3957, -1.3441, 30]}, {"name": "command", "type": "integer", "value": 16}, {"name": "param1", "type": "integer"}, {"name": "param2", "type": "integer"}, {"name": "param3", "type": "integer"}, {"name": "param4", "type": "integer"}]}]}
        cmds = inVehicle.commands
        cmds.download()
        cmds.wait_ready()
        my_logger.debug("Mission Commands")
        # Save the vehicle commands to a list
        missionlist = []
        for cmd in cmds:
            autoContinue = True
            if (cmd.autocontinue == 0):
                autoContinue = False
            missionlist.append({'id': cmd.seq, "autoContinue": autoContinue, "command": cmd.command, "coordinate": [
                               cmd.x, cmd.y, cmd.z], 'frame': cmd.frame, 'param1': cmd.param1, 'param2': cmd.param2, 'param3': cmd.param3, 'param4': cmd.param4})
            my_logger.debug(cmd)
        my_logger.debug(missionlist)
        outputObj['items'] = missionlist
        outputObj['plannedHomePosition'] = {
            'id': 0,
            'autoContinue': True,
            'command': 16,
            "coordinate": [
                inVehicle.home_location.lat,
                inVehicle.home_location.lon,
                0],
            'frame': 0,
            'param1': 0,
            'param2': 0,
            'param3': 0,
            'param4': 0}
        outputObj['version'] = '1.0'
        outputObj['MAV_AUTOPILOT'] = 3
        outputObj['complexItems'] = []
        outputObj['groundStation'] = 'QGroundControl'
        outputObj["_links"] = {
            "self": {
                "href": droneAPIUtils.homeDomain +
                "/vehicle/" +
                str(vehicle_id) +
                "/mission",
                "title": "Get the current mission commands from the vehicle."}}

        # outputObj['mission']=cmds
        output = json.dumps(outputObj)
    except Exception as ex:  # pylint: disable=W0703
        my_logger.exception(ex)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")
        return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
    return output
