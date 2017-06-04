#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math
import droneAPIMain, droneAPIUtils

my_logger = droneAPIMain.my_logger




class authorizedZone:        

    def POST(self,vehicleId):
        try:
            my_logger.info( "#### Method POST of authorizedZone ####")
            my_logger.debug( "vehicleId = '"+vehicleId+"'")
            droneAPIUtils.applyHeadders()
            try:
                inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            vehicleStatus=droneAPIUtils.getVehicleStatus(inVehicle)
            my_logger.info(vehicleStatus)
            data = json.loads(web.data())
            zone = data["zone"]
            #validate and enrich data
            if (zone["shape"]["name"]=="circle"):
                if (zone.get("lat",-1)==-1): #if there is no lat,lon add current location as default
                    zone["shape"]["lat"]=vehicleStatus["global_frame"]["lat"]
                    zone["shape"]["lon"]=vehicleStatus["global_frame"]["lon"]
                    zone["shape"]["radius"]=500; #default radius of 500
            outputObj={}
            outputObj["zone"]=zone
            droneAPIMain.authorizedZoneDict[vehicleId]=zone
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)


