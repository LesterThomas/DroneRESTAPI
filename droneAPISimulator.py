# This class handles the '/vehicle/(.*)/simulator' resource end-point which manages the Drone Simulator paramaters

import logging
import traceback
import json
import droneAPIUtils
import web

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class simulator:
    def GET(self, vehicleId):
        try:
            my_logger.info("GET: vehicleId=" + str(vehicleId))
            my_logger.debug("vehicleId = '" + vehicleId + "'")
            droneAPIUtils.applyHeadders()
            output = getSimulatorParams(vehicleId)
            my_logger.info("Return: =" + output)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info("POST: vehicleId=" + str(vehicleId))
            droneAPIUtils.applyHeadders()
            try:
                inVehicle = droneAPIUtils.connectVehicle(vehicleId)
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicleId)})
            my_logger.debug("posting new simulator parameter")
            simulatorData = json.loads(web.data())
            my_logger.debug(simulatorData)
            simKey = str(simulatorData['parameter'])
            simValue = simulatorData['value']
            my_logger.debug(simKey)
            my_logger.debug(simValue)
            inVehicle.parameters[simKey] = simValue
            my_logger.debug('Updated parameter')

            output = getSimulatorParams(vehicleId)
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
            # just here to suppor the CORS Cross-Origin security
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


def getSimulatorParams(vehicleId):
    try:
        try:
            inVehicle = droneAPIUtils.connectVehicle(vehicleId)
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
            return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
        except Exception as e:
            my_logger.exception(e)
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
            return json.dumps({"error": "Cant connect to vehicle " + str(vehicleId)})
        vehicleStatus = droneAPIUtils.getVehicleStatus(inVehicle, vehicleId)
        outputObj = {"_actions": [{"method": "POST", "title": "Upload a new simulator paramater to the simulator. ", "fields": [
            {"name": "parameter", "value": "SIM_WIND_SPD", "type": "string"}, {"name": "value", "type": "integer", "float": 10}]}]};

        simulatorParams = {}

        my_logger.debug("Simulator Parameters")
        my_logger.debug(inVehicle.parameters)

        for key, value in inVehicle.parameters.iteritems():
            my_logger.debug(" Key:" + str(key) + " Value:" + str(value))
            my_logger.debug(key.find("SIM"))
            if (key.find("SIM") == 0):
                simulatorParams[key] = inVehicle.parameters[key]

        outputObj['simulatorParams'] = simulatorParams
        outputObj["_links"] = {
            "self": {
                "href": droneAPIUtils.homeDomain +
                "/vehicle/" +
                str(vehicleId) +
                "/simulator",
                "title": "Get the current simulator parameters from the vehicle."},
            "up": {
                "href": droneAPIUtils.homeDomain +
                "/vehicle/" +
                str(vehicleId),
                "title": "Get status for parent vehicle."}}

        # outputObj['mission']=cmds
        output = json.dumps(outputObj)
    except Exception as e:
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")
        return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
    return output
