#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math
import  droneAPIUtils

my_logger = logging.getLogger("DroneAPIServer."+str(__name__))


class action:     
    def OPTIONS(self, vehicleId):
        try:
            my_logger.info( "OPTIONS: vehicleId="+str(vehicleId))
            droneAPIUtils.applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
            my_logger.info( "Return: ="+output )

        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


    def GET(self, vehicleId):
        try:
            my_logger.info("GET: vehicleId="+str(vehicleId))

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
            outputObj={}
            outputObj["_links"]={"self":{"href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action","title":"Get the actions for this vehicle."}}
            availableActions=[]
            #available when armed
            my_logger.info("global_relative_frame.alt=%s",vehicleStatus["global_relative_frame"]["alt"])
            if (vehicleStatus["global_relative_frame"]["alt"]>1):  #if at height of >1 m
                availableActions.append({   
                    "name":"Region-of-Interest",
                    "title":"Set a Region of Interest : When the drone is flying, it will face the point  <lat>,<lon>,<alt> (defaults to the home location)",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Region-of-Interest"},{"name":"lat","type":"float","value":51.3946},{"name":"lon","type":"float","value":-1.299},{"name":"alt","type":"float","value":105}]
                })
                availableActions.append({   
                    "name":"Land",
                    "title":"Land at current location",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Land"}]
                })
                availableActions.append({   
                    "name":"Return-to-Launch",
                    "title":"Return to launch: Return to the home location and land.",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Return-to-Launch"}]
                })
                availableActions.append({   
                    "name":"Start-Mission",
                    "title":"Begin the pre-defined mission.",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Start-Mission"}]
                })
                availableActions.append({   
                    "name":"Goto-Absolute",
                    "title":"Go to the location at latitude <lat>, longitude <lon> and altitude <alt> (above sea level).",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Goto-Absolute"},{"name":"lat","type":"float","value":51.3946},{"name":"lon","type":"float","value":-1.299},{"name":"alt","type":"float","value":105}]
                })
                availableActions.append({   
                    "name":"Goto-Relative-Home",
                    "title":"Go to the location <north> meters North, <east> meters East and <up> meters vertically from the home location.",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Goto-Relative-Home"},{"name":"north","type":"float","value":30},{"name":"east","type":"float","value":30},{"name":"up","type":"float","value":10}]
                })
                availableActions.append({   
                    "name":"Goto-Relative-Current",
                    "title":"Go to the location <north> meters North, <east> meters East and <up> meters vertically from the current location.",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Goto-Relative-Current"},{"name":"north","type":"float","value":30},{"name":"east","type":"float","value":30},{"name":"up","type":"float","value":10}]
                })
            elif vehicleStatus["armed"]:
                availableActions.append({   
                    "name":"Takeoff",
                    "title":"Takeoff in GUIDED mode to height of <height> (default 20m).",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Takeoff"},{"name":"height","type":"float","value":30}]
                })
            else :
                availableActions.append({   
                    "name":"Arm",
                    "title":"Arm drone.",
                    "href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                    "method":"POST",
                    "fields":[{"name":"name","type":"string","value":"Arm"}]
                })
            outputObj['_actions']=availableActions
            my_logger.debug(outputObj)
            updateActionStatus(inVehicle, vehicleId);
            outputObj['actions']=droneAPIUtils.actionArrayDict[vehicleId]
            output=json.dumps(outputObj)   
            my_logger.info( "Return: ="+output )
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def POST(self, vehicleId):
        try:
            my_logger.info( "POST: vehicleId="+str(vehicleId))
            try:
                inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up ", "_actions": actions}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId), "_actions": actions}) 
            droneAPIUtils.applyHeadders()
            data = json.loads(web.data())
            #get latest data (inc homeLocation from vehicle)
            my_logger.debug( "Getting commands:")

            cmds = inVehicle.commands
            my_logger.debug( "Download:")

            cmds.download()
            my_logger.debug( "Wait until ready:")
            cmds.wait_ready() 


            my_logger.debug( "Data:")
            my_logger.debug( data)
            value = data["name"]
            my_logger.debug( "Value:")
            my_logger.debug( value)
            outputObj={}
            if value=="Return-to-Launch":
                outputObj["action"]=rtl(inVehicle)
            elif value=="Arm":
                my_logger.debug( "Armiong")
                outputObj["action"]=arm(inVehicle)
            elif value=="Takeoff":
                height=data.get("height",20) #get height - default to 20
                my_logger.debug( "Taking off to height of " + str(height))
                outputObj["action"]=takeoff(inVehicle,height)
            elif value=="Start-Mission":
                outputObj["action"]=auto(inVehicle)
            elif value=="Land":
                outputObj["action"]=land(inVehicle)
            elif value=="Goto-Absolute":
                defaultLocation=inVehicle.location.global_frame #default to current position
                my_logger.debug( "Global Frame" + str(defaultLocation))
                inLat=data.get("lat",defaultLocation.lat)
                inLon=data.get("lon",defaultLocation.lon)
                inAlt=data.get("alt",defaultLocation.alt)
                locationObj={'lat':float(inLat), 'lon':float(inLon), 'alt':float(inAlt)}
                outputObj["action"]=gotoAbsolute(inVehicle,locationObj)
            elif value=="Goto-Relative-Home":
                inNorth=float(data.get("north",0))
                inEast=float(data.get("east",0))
                inDown=-float(data.get("up",0))
                my_logger.debug( "Goto-Relative-Home" )
                my_logger.debug( inNorth)
                my_logger.debug( inEast)
                my_logger.debug( inDown)
                outputObj["action"]=gotoRelative(inVehicle,inNorth,inEast,inDown)
            elif value=="Goto-Relative-Current":
                inNorth=float(data.get("north",0))
                inEast=float(data.get("east",0))
                inDown=-float(data.get("up",0))
                outputObj["action"]=goto(inVehicle,inNorth,inEast,inDown)
            elif value=="Region-of-Interest":
                cmds = inVehicle.commands
                cmds.download()
                cmds.wait_ready()
                defaultLocation=inVehicle.home_location
                inLat=data.get("lat",defaultLocation.lat)
                inLon=data.get("lon",defaultLocation.lon)
                inAlt=data.get("alt",defaultLocation.alt)
                locationObj={'lat':float(inLat), 'lon':float(inLon), 'alt':float(inAlt)}
                outputObj["action"]=roi(inVehicle,locationObj)
            else:
                outputObj["action"]={"status":"error", "name":value, "error":"No action found with name '" + value+ "'." }
            actionArray=droneAPIUtils.actionArrayDict[vehicleId]
            if (len(actionArray)==0):
                outputObj['action']['id']=0;
            else:
                outputObj['action']['id']=actionArray[len(actionArray)-1]['action']['id']+1
            actionArray.append(outputObj)
            if (len(actionArray)>10):
                actionArray.pop(0)
            outputObj['href']=droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId)+"/action"
            my_logger.info( "Return: ="+json.dumps(outputObj) )

        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             


        return json.dumps(outputObj)



#methods to support the different actions
def rtl(inVehicle):        
     
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Return-to-Launch"
        outputObj["status"]="success"
        #coodinates are same as home
        homeLocation=inVehicle.home_location
        outputObj["coordinate"]=[homeLocation.lat, homeLocation.lon, homeLocation.alt]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=20
        my_logger.info( "Returning to Launch")
        inVehicle.mode = VehicleMode("RTL")
    else:
        outputObj["name"]="Return-to-Launch"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
        my_logger.warn( "RTL error - Vehicle not armed")

    return outputObj  

def arm(inVehicle,):        
    outputObj={}
    if inVehicle.is_armable:
        outputObj["name"]="Arm"
        outputObj["status"]="success"
        #coodinates are same as current + height
        currentLocation=inVehicle.location.global_relative_frame
        outputObj["coordinate"]=[currentLocation.lat, currentLocation.lon, 0]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=22
        my_logger.info( "Arming motors")
        # Copter should arm in GUIDED mode
        inVehicle.mode    = VehicleMode("GUIDED")
        inVehicle.armed   = True
        # Confirm vehicle armed before attempting to take off
        while not inVehicle.armed:
            my_logger.info( " Waiting for arming..."  )
            time.sleep(1)
    else:
        outputObj["name"] = "Arm"
        outputObj["status"] = "Error"
        outputObj["error"] = "vehicle not armable"
        my_logger.warn( "vehicle not armable")
    return outputObj

def takeoff(inVehicle, inHeight):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Takeoff"
        outputObj["height"]=inHeight
        outputObj["status"]="success"
        #coodinates are same as current + height
        currentLocation=inVehicle.location.global_relative_frame
        outputObj["coordinate"]=[currentLocation.lat, currentLocation.lon, inHeight]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=22
        my_logger.info( "Arming motors")
        inVehicle.mode    = VehicleMode("GUIDED")
        my_logger.info( "Taking off!")
        inVehicle.simple_takeoff(inHeight) # Take off to target altitude
    else:
        outputObj["name"] = "Takeoff"
        outputObj["status"] = "Error"
        outputObj["error"] = "vehicle not armable"
        my_logger.warn( "vehicle not armable")
    return outputObj

def auto(inVehicle):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Start-Mission"
        outputObj["status"]="success"
        my_logger.info( "Auto mission")
        if inVehicle.mode.name=="AUTO":
            #vehicle already in auto mode - swap it into GUIDED first.
            inVehicle.mode    = VehicleMode("GUIDED")
            time.sleep(1)
        inVehicle.mode = VehicleMode("AUTO")
    else:    
        outputObj["name"]="Start-Mission"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def land(inVehicle):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Land"
        outputObj["status"]="success"
        #coodinates are same as current 
        currentLocation=inVehicle.location.global_relative_frame
        outputObj["coordinate"]=[currentLocation.lat, currentLocation.lon, 0]
        outputObj["param1"]=0
        outputObj["param2"]=0
        outputObj["param3"]=0
        outputObj["param4"]=0
        outputObj["command"]=23
        my_logger.info( "Landing")
        inVehicle.mode = VehicleMode("LAND")
    else:    
        outputObj["name"]="Land"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def goto(inVehicle, dNorth, dEast, dDown):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
    """
    global config
    outputObj={}
    if inVehicle.armed:
        distance=round(math.sqrt(dNorth*dNorth+dEast*dEast))
        my_logger.info("Goto a distance of " + str(distance) + "m.")
        if distance>1000:
            outputObj["status"]="Error"
            outputObj["error"]="Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            outputObj["name"]="Max-Distance-Error"
        else:
            outputObj["name"]="Goto-Relative-Current"
            outputObj["status"]="success"
            inVehicle.mode = VehicleMode("GUIDED")
            currentLocation = inVehicle.location.global_relative_frame
            targetLocation = get_location_metres(currentLocation, dNorth, dEast)
            targetLocation.alt=targetLocation.alt-dDown
            #coodinates are target
            outputObj["coordinate"]=[targetLocation.lat, targetLocation.lon, targetLocation.alt]
            outputObj["param1"]=0
            outputObj["param2"]=0
            outputObj["param3"]=0
            outputObj["param4"]=0
            outputObj["command"]=16
            inVehicle.simple_goto(targetLocation, groundspeed=10)
    else:    
        outputObj["name"]="Goto-Relative-Current"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.
    """
    my_logger.debug( "lat:" + str(original_location.lat) + " lon:" + str(original_location.lon))
    my_logger.debug( "north:" + str(dNorth) + " east:" + str(dEast))
     
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    if type(original_location) is LocationGlobal:
        targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
    else:
        raise Exception("Invalid Location object passed")
    return targetlocation;

def gotoRelative(inVehicle, north, east, down):
    global config
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Goto-Relative-Home"
        outputObj["status"]="success"
        inVehicle.mode = VehicleMode("GUIDED")

        homeLocation=inVehicle.home_location

        #currentLocation = inVehicle.location.global_relative_frame
        targetLocation = get_location_metres(homeLocation, north, east)
        targetLocation.alt=homeLocation.alt-down
        distance=round(droneAPIUtils.distanceInMeters(targetLocation.lat,targetLocation.lon,inVehicle.location.global_frame.lat,inVehicle.location.global_frame.lon))
        if distance>1000:
            outputObj["status"]="Error"
            outputObj["error"]="Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            outputObj["name"]="Max-Distance-Error"
        else:
            #coodinates are target
            outputObj["coordinate"]=[targetLocation.lat, targetLocation.lon, -down]
            outputObj["param1"]=0
            outputObj["param2"]=0
            outputObj["param3"]=0
            outputObj["param4"]=0
            outputObj["command"]=16  
            inVehicle.simple_goto(targetLocation, groundspeed=10)
    else:    
        outputObj["name"]="Goto-Relative-Home"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj


def gotoAbsolute(inVehicle, inLocation):        
    global config
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="Goto-Absolute"
        outputObj["status"]="success"
        my_logger.debug( " Goto Location: %s" % inLocation   )  
        output = {"global_frame":inLocation}
        my_logger.debug( "lat" + str(inLocation['lat']))

        distance=round(droneAPIUtils.distanceInMeters(inLocation['lat'], inLocation['lon'],inVehicle.location.global_frame.lat,inVehicle.location.global_frame.lon))
        if distance>1000:
            outputObj["status"]="Error"
            outputObj["error"]="Can not go more than " + str(1000) + "m in single command. Action was to go " + str(distance) + " m."
            outputObj["name"]="Max-Distance-Error"
        else:
            inVehicle.mode = VehicleMode("GUIDED")
            #coodinates are target
            outputObj["coordinate"]=[inLocation['lat'], inLocation['lon'], inLocation['alt']]
            outputObj["param1"]=0
            outputObj["param2"]=0
            outputObj["param3"]=0
            outputObj["param4"]=0
            outputObj["command"]=16

            inVehicle.simple_goto(LocationGlobal(inLocation['lat'],inLocation['lon'],inLocation['alt']), groundspeed=10)
    else:    
        outputObj["name"]="Goto-Absolute"
        outputObj["status"]="Error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def roi(inVehicle, inLocation):        
    outputObj={}
    outputObj["name"]="Region-of-Interest"
    outputObj["status"]="success"
    my_logger.debug( " Home Location: %s" % inLocation     )
    output = {"home_location":inLocation}
    my_logger.debug( "lat" + str(inLocation['lat']))
    #coodinates are target
    outputObj["coordinate"]=[inLocation['lat'],inLocation['lon'],inLocation['alt']]
    outputObj["param1"]=0
    outputObj["param2"]=0
    outputObj["param3"]=0
    outputObj["param4"]=0
    outputObj["command"]=80  
    set_roi(inVehicle, inLocation)
    return outputObj

def set_roi(inVehicle, location):
    # create the MAV_CMD_DO_SET_ROI command
    msg = inVehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
        0, #confirmation
        0, 0, 0, 0, #params 1-4
        location['lat'],
        location['lon'],
        location['alt']
        )
    # send command to vehicle
    inVehicle.send_mavlink(msg)



def updateActionStatus(inVehicle, inVehicleId):
    #test to see whether the vehicle is at the target location of the action
    my_logger.info("############# in updateActionStatus")

    my_logger.info("inVehicleId")
    my_logger.info(inVehicleId)
    my_logger.info("droneAPIUtils.actionArrayDict")
    my_logger.info(droneAPIUtils.actionArrayDict)
    my_logger.info("#############")

    actionArray=droneAPIUtils.actionArrayDict[inVehicleId]


    my_logger.info(actionArray)

    if (len(actionArray)>0):
        latestAction=actionArray[len(actionArray)-1]

        if (latestAction['action']['status']=="Error"):
            latestAction['complete']=False
            latestAction['completeStatus']='Error'
            return
        my_logger.debug("Latest Action:" + latestAction['action']['name'])

        if (latestAction['action']['name']=='Start-Mission'):
            #cant monitor progress at the moment
            my_logger.info("Cant monitor progress for mission")
        else:
            my_logger.debug("Monitoring progress for action '" + latestAction['action']['name'] + "'")

            targetCoordinates=latestAction['action']['coordinate'] #array with lat,lon,alt
            my_logger.info(inVehicle)
            vehicleCoordinates=inVehicle.location.global_relative_frame #object with lat,lon,alt attributes
            #Return-to-launch uses global_frame (alt is absolute)
            
            if (latestAction['action']['name']=='Return-to-Launch'):
                vehicleCoordinates=inVehicle.location.global_frame #object with lat,lon,alt attributes

            horizontalDistance=droneAPIUtils.distanceInMeters(targetCoordinates[0],targetCoordinates[1],vehicleCoordinates.lat,vehicleCoordinates.lon)
            verticalDistance=abs(targetCoordinates[2]-vehicleCoordinates.alt)
            latestAction['horizontalDistance']=round(horizontalDistance,2)
            latestAction['verticalDistance']=round(verticalDistance,2)
            if ((horizontalDistance<5) and (verticalDistance<1)):
                latestAction['complete']=True
                latestAction['completeStatus']='Complete'
            else:
                latestAction['completeStatus']='In progress'
                latestAction['complete']=False
            #region of interest is special case
            if (latestAction['action']['name']=='Region-of-Interest'):
                latestAction['complete']=True
                latestAction['completeStatus']='Complete'

    if (len(actionArray)>1): #check if previous actions completed or were interrupted
        previousAction=actionArray[len(actionArray)-2]
        if (previousAction.get('complete',False)==False):
            if (previousAction.get('completeStatus','In progress')=="In progress"):
                previousAction['completeStatus']='Interrupted'
                previousAction['complete']=False

           

    return
