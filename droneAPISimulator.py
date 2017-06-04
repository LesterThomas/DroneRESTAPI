#This class handles the '/vehicle/(.*)/simulator' resource end-point which manages the Drone Simulator paramaters

import logging, traceback, json
import droneAPIMain

my_logger = droneAPIMain.my_logger


class simulator:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of simulator ####")
            my_logger.debug( "vehicleId = '"+vehicleId+"'")
            droneAPIMain.applyHeadders()
            output=getSimulatorParams(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info( "#### Method POST of simulator ####")
            droneAPIMain.applyHeadders()
            try:
                inVehicle=droneAPIMain.connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
            my_logger.info( "posting new simulator parameter")
            simulatorData = json.loads(web.data());
            my_logger.info(simulatorData);
            simKey=str(simulatorData['parameter'])
            simValue=simulatorData['value']
            my_logger.info(simKey);
            my_logger.info(simValue);
            inVehicle.parameters[simKey]=simValue;
            my_logger.info('Updated parameter');
           
            output=getSimulatorParams(vehicleId) 
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self, vehicleId):
        try:
            my_logger.info( "#### Method OPTIONS of simulator - just here to suppor the CORS Cross-Origin security ####")
            droneAPIMain.applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

def getSimulatorParams(vehicleId) :
    try:
        try:
            inVehicle=droneAPIMain.connectVehicle(vehicleId)   
        except Warning:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle - vehicle starting up "}) 
        except Exception:
            my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
            return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId)}) 
        vehicleStatus=droneAPIMain.getVehicleStatus(inVehicle)
        outputObj={"_actions":[{"method":"POST","title":"Upload a new simulator paramater to the simulator. ", "fields":[ {"name":"parameter","value":"SIM_WIND_SPD","type":"string"},{"name":"value","type":"integer","float":10}]}]};

        simulatorParams={}

        my_logger.debug( "Simulator Parameters")
        my_logger.debug( inVehicle.parameters)

        for key, value in inVehicle.parameters.iteritems():
            my_logger.debug( " Key:"+str(key)+" Value:" + str(value))
            my_logger.debug( key.find("SIM"))
            if (key.find("SIM")==0):
                simulatorParams[key]=inVehicle.parameters[key]

        outputObj['simulatorParams']=simulatorParams
        outputObj["_links"]={"self":{"href":droneAPIMain.homeDomain+"/vehicle/"+str(vehicleId)+"/simulator","title":"Get the current simulator parameters from the vehicle."},
            "up":{"href":droneAPIMain.homeDomain+"/vehicle/"+str(vehicleId),"title":"Get status for parent vehicle."}}


 
        #outputObj['mission']=cmds
        output=json.dumps(outputObj)   
    except Exception as e: 
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")   
        return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
    return output

