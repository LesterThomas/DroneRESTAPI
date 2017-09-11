"""This module provides the API endpoint to retrieve the home location for a drone. The home
location is the position the drone took off from."""


import logging
import traceback
import json
import droneAPIUtils
import redis
import web

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class homeLocation:

    def __init__(self):
        return

    def GET(self, vehicleId):
        try:
            my_logger.info("GET: vehicleId=" + str(vehicleId))
            statusVal = ''  # removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug("vehicleId = '" + vehicleId + "', statusVal = '" + statusVal + "'")
            droneAPIUtils.applyHeadders()
            query_parameters = web.input()
            user_id = query_parameters['user_id']

            try:
                inVehicle = droneAPIUtils.connectVehicle(user_id, vehicleId)
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error": "Cant connect to vehicle - vehicle starting up "})
            except Exception:  # pylint: disable=W0703
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error": "Cant connect to vehicle " + str(vehicleId)})
            droneAPIUtils.getVehicleStatus(inVehicle, vehicleId)
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            my_logger.debug(" Home Location: %s", inVehicle.home_location)
            output = json.dumps(
                {
                    "_links": {
                        "self": {
                            "href": droneAPIUtils.homeDomain +
                            "/vehicle/" +
                            str(vehicleId) +
                            "/homeLocation",
                            "title": "Get the home location for this vehicle"}},
                    "home_location": droneAPIUtils.latLonAltObj(
                        inVehicle.home_location)})
            my_logger.info("Return: =" + output)

        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return output
