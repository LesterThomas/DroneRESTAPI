"""This module provides the API endpoint to manage the zones a drone is authorised to fly in. The
existing authorized zones are returned as part of the vehicleStatus. This module allows you
to request a new authorised zone."""


import web
import logging
import traceback
import json
import droneAPIUtils


my_logger = logging.getLogger("DroneAPIWorker." + str(__name__))


class authorizedZone:

    def __init__(self):
        return

    def POST(self, vehicle_id):
        try:
            my_logger.info("POST: vehicle_id=" + str(vehicle_id))
            my_logger.debug("vehicle_id = '" + vehicle_id + "'")
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
            vehicleStatus = droneAPIUtils.getVehicleStatus(inVehicle, vehicle_id)
            my_logger.info(vehicleStatus)
            data = json.loads(web.data())
            zone = data["zone"]
            # validate and enrich data
            if (zone["shape"]["name"] == "circle"):
                if (zone.get("lat", -1) == -1):  # if there is no lat,lon add current location as default
                    zone["shape"]["lat"] = vehicleStatus["global_frame"]["lat"]
                    zone["shape"]["lon"] = vehicleStatus["global_frame"]["lon"]
                    zone["shape"]["radius"] = 500  # default radius of 500
            outputObj = {}
            outputObj["zone"] = zone
            droneAPIUtils.authorizedZoneDict[vehicle_id] = zone
            my_logger.info("Return: =" + json.dumps(outputObj))
        except Exception as ex:  # pylint: disable=W0703
            my_logger.exception(ex)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": ex.message, "args": ex.args, "traceback": traceLines})
        return json.dumps(outputObj)
