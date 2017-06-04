#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math
import droneAPIMain, droneAPIUtils

my_logger = droneAPIMain.my_logger



class mission:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of mission ####")
            my_logger.debug( "vehicleId = '"+vehicleId+"'")
            droneAPIUtils.applyHeadders()
            output=getMissionActions(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info( "#### Method POST of mission ####")
            droneAPIUtils.applyHeadders()
            try:
                inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            #download existing commands
            my_logger.info( "download existing commands")
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            #clear the commands
            my_logger.info( "clearing existing commands")
            cmds.clear()
            inVehicle.flush()
            missionActionArray = json.loads(web.data())
            my_logger.info( "missionCommandArray:")
            my_logger.info( missionActionArray)
            #add new commands
            for missionAction in missionActionArray:
                my_logger.info(missionAction)
                lat = missionAction['coordinate'][0]
                lon = missionAction['coordinate'][1]
                altitude = missionAction['coordinate'][2]
                cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, missionAction['command'],
                    0, 0, missionAction['param1'], missionAction['param2'], missionAction['param3'], missionAction['param4'],
                    lat, lon, altitude)
                my_logger.info( "Add new command with altitude:")
                my_logger.info( altitude)
                cmds.add(cmd)
            inVehicle.flush()
            my_logger.info( "Command added")
            output=getMissionActions(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self, vehicleId):
        try:
            my_logger.info( "#### Method OPTIONS of mission - just here to suppor the CORS Cross-Origin security ####")
            droneAPIUtils.applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


def getMissionActions(vehicleId) :
    try:
        try:
            inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
        except Exception:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
        vehicleStatus=droneAPIUtils.getVehicleStatus(inVehicle)
        outputObj={"_actions":[{"name":"upload mission","method":"POST","title":"Upload a new mission to the vehicle. The mission is a collection of mission actions with <command>, <coordinate[lat,lon,alt]> and command specific <param1>,<param2>,<param3>,<param4>. The command-set is described at https://pixhawk.ethz.ch/mavlink/", 
                "fields": [{"name":"coordinate", "type":"array","value":[51.3957,-1.3441,30]},{"name":"command","type":"integer","value":16},
                {"name":"param1","type":"integer"},{"name":"param2","type":"integer"},{"name":"param3","type":"integer"},{"name":"param4","type":"integer"}]}]}
        cmds = inVehicle.commands
        cmds.download()
        cmds.wait_ready()
        my_logger.debug( "Mission Commands")
        # Save the vehicle commands to a list
        missionlist=[]
        for cmd in cmds:
            autoContinue=True
            if (cmd.autocontinue==0):
                autoContinue=False
            missionlist.append({'id':cmd.seq,"autoContinue": autoContinue ,"command": cmd.command,"coordinate": [cmd.x,cmd.y,cmd.z],'frame':cmd.frame,'param1':cmd.param1,'param2':cmd.param2,'param3':cmd.param3,'param4':cmd.param4})
            my_logger.debug( cmd)
        my_logger.debug( missionlist)
        outputObj['items']=missionlist
        outputObj['plannedHomePosition']={'id':0,'autoContinue':True,'command':16,"coordinate": [inVehicle.home_location.lat,inVehicle.home_location.lon,0], 'frame':0,'param1':0,'param2':0,'param3':0,'param4':0}
        outputObj['version']='1.0'
        outputObj['MAV_AUTOPILOT']=3
        outputObj['complexItems']=[]
        outputObj['groundStation']='QGroundControl'
        outputObj["_links"]={"self":{"href":droneAPIMain.homeDomain+"/vehicle/"+str(vehicleId)+"/mission","title":"Get the current mission commands from the vehicle."}}

        #outputObj['mission']=cmds
        output=json.dumps(outputObj)   
    except Exception as e: 
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")   
        return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
    return output