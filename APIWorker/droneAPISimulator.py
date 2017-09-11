"""This module provides the API endpoint for simulated drones to manage the simulator parameters"""

# This class handles the '/vehicle/(.*)/simulator' resource end-point which manages the Drone Simulator paramaters

import logging
import traceback
import json
import droneAPIUtils
import web

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class simulator:

    def __init__(self):
        return

    def GET(self, vehicle_id):
        try:
            my_logger.info("GET: vehicle_id=" + str(vehicle_id))
            my_logger.debug("vehicle_id = '" + vehicle_id + "'")
            droneAPIUtils.applyHeadders()
            query_parameters = web.input()
            user_id=query_parameters['user_id']
            output = getSimulatorParams(user_id, vehicle_id)
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
                user_id=data["user_id"]
                inVehicle = droneAPIUtils.connectVehicle(user_id,vehicle_id)
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
            except Exception:  # pylint: disable=W0703
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicle_id))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicle_id)})
            my_logger.debug("posting new simulator parameter")
            simulatorData = json.loads(web.data())
            my_logger.debug(simulatorData)
            simKey = str(simulatorData['parameter'])
            simValue = simulatorData['value']
            my_logger.info(simKey)
            my_logger.info(simValue)
            inVehicle.parameters[simKey] = float(simValue)
            my_logger.debug('Updated parameter')

            output = getSimulatorParams(user_id,vehicle_id)
            my_logger.info("Return: =" + output)
        except Exception as ex:
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output

    def OPTIONS(self, vehicle_id):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS: vehicle_id=" + str(vehicle_id))
            # just here to suppor the CORS Cross-Origin security
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


def getSimulatorParams(user_id, vehicle_id):
    try:
        try:
            inVehicle = droneAPIUtils.connectVehicle(user_id, vehicle_id)
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicle_id))
            return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicle_id))
            return json.dumps({"error": "Cant connect to vehicle " + str(vehicle_id)})
        droneAPIUtils.getVehicleStatus(inVehicle, vehicle_id)
        outputObj = {"_actions": [{"method": "POST", "title": "Upload a new simulator paramater to the simulator. ", "fields": [
            {"name": "parameter", "value": "SIM_WIND_SPD", "type": "string"}, {"name": "value", "type": "integer", "float": 10}]}]}

        simulatorParams = {}

        my_logger.debug("Simulator Parameters")
        my_logger.debug(inVehicle.parameters)

        for key, value in inVehicle.parameters.iteritems():
            my_logger.debug(" Key:" + str(key) + " Value:" + str(value))
            my_logger.debug(key.find("SIM"))
            if (key.find("SIM") == 0):
                simulatorParams[key] = inVehicle.parameters[key]
            if (key.find("TERRAIN") == 0):
                simulatorParams[key] = inVehicle.parameters[key]

        outputObj['simulatorParams'] = simulatorParams
        outputObj["_links"] = {
            "self": {
                "href": droneAPIUtils.homeDomain +
                "/vehicle/" +
                str(vehicle_id) +
                "/simulator",
                "title": "Get the current simulator parameters from the vehicle."},
            "up": {
                "href": droneAPIUtils.homeDomain +
                "/vehicle/" +
                str(vehicle_id),
                "title": "Get status for parent vehicle."}}

        # outputObj['mission']=cmds
        output = json.dumps(outputObj)
    except Exception as ex:  # pylint: disable=W0703
        my_logger.exception(ex)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")
        return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
    return output
