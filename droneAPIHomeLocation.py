#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math
import droneAPIMain, droneAPIUtils

my_logger = droneAPIMain.my_logger



class homeLocation:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of homeLocation ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            droneAPIUtils.applyHeadders()
            outputObj={}
            try:
                inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            vehicleStatus=droneAPIUtils.getVehicleStatus(inVehicle)
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            my_logger.debug( " Home Location: %s" % inVehicle.home_location     )
            output = json.dumps({"_links":{"self":{"href":droneAPIMain.homeDomain+"/vehicle/"+str(vehicleId)+"/homeLocation","title":"Get the home location for this vehicle"}},"home_location":droneAPIUtils.latLonAltObj(inVehicle.home_location)}   )   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

