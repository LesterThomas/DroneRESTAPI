#!/usr/bin/env python

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, mavutil
import time
import json
import math

import web

connectionStringArray = ["","udp:127.0.0.1:14551"] #["","udp:10.0.0.2:6000","udp:127.0.0.1:14561","udp:127.0.0.1:14571","udp:127.0.0.1:14581"]  #for drones 1-4
connectionArray=[None ,None]

def applyHeadders():
    print "Applying HTTP headers"
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin',      '*')
    web.header('Access-Control-Allow-Credentials', 'true')        
    web.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')   
    web.header('Access-Control-Allow-Headers', 'Content-Type')      
    return

def connectVehicle(inVehicleId):
    global connectionStringArray
    global connectionArray
    print ""
    print "connectVehicle called with inVehicleId = " + str(inVehicleId)
    try:
        connectionString=connectionStringArray[int(inVehicleId)]
    except ValueError:
        print inVehicleId + " is not an Integer"
        return 

    # Connect to the Vehicle.
    if not connectionArray[int(inVehicleId)]:
        print("connectionString: %s" % (connectionString,))
        print("Connecting to vehicle on: %s" % (connectionString,))
        connectionArray[int(inVehicleId)] = connect(connectionString, wait_ready=True)
    else:
        print "Already connected to vehicle" 

    return connectionArray[int(inVehicleId)]

def latLonAltObj(inObj):
    output={}
    output["lat"]=(inObj.lat)
    output["lon"]=(inObj.lon)
    output["alt"]=(inObj.alt)
    return output

#methods to support the different actions
def rtl(inVehicle):        
     
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="rtl"
        outputObj["status"]="success"
        print "Returning to Launch"
        inVehicle.mode = VehicleMode("RTL")
    else:
        outputObj["name"]="rtl"
        outputObj["status"]="error"
        outputObj["error"]="Vehicle not armed"

    return outputObj  

def takeoff(inVehicle, inHeight):        
    outputObj={}
    if inVehicle.is_armable:
        outputObj["name"]="takeoff"
        outputObj["status"]="success"
        print "Arming motors"
        # Copter should arm in GUIDED mode
        inVehicle.mode    = VehicleMode("GUIDED")
        inVehicle.armed   = True
        # Confirm vehicle armed before attempting to take off
        while not inVehicle.armed:
            print " Waiting for arming..."  
            time.sleep(1)
        print "Taking off!"
        inVehicle.simple_takeoff(inHeight) # Take off to target altitude
    else:
        outputObj["name"] = "takeoff"
        outputObj["status"] = "error"
        outputObj["error"] = "vehicle not armable"
        print "vehicle not armable"
    return outputObj

def auto(inVehicle):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="auto"
        outputObj["status"]="success"
        print "Auto mission"
        inVehicle.mode = VehicleMode("AUTO")
    else:    
        outputObj["name"]="auto"
        outputObj["status"]="error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def land(inVehicle):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="land"
        outputObj["status"]="success"
        print "Landing"
        inVehicle.mode = VehicleMode("LAND")
    else:    
        outputObj["name"]="land"
        outputObj["status"]="error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def goto(inVehicle, dNorth, dEast, dDown):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
    """
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="gotoRelativeCurrent"
        outputObj["status"]="success"
        currentLocation = inVehicle.location.global_relative_frame
        targetLocation = get_location_metres(currentLocation, dNorth, dEast)
        targetLocation.alt=targetLocation.alt-dDown
        inVehicle.simple_goto(targetLocation, groundspeed=10)
    else:    
        outputObj["name"]="gotoRelativeCurrent"
        outputObj["status"]="error"
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
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="gotoRelativeHome"
        outputObj["status"]="success"
        #vehicle.mode = VehicleMode("GUIDED")
        msg = inVehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
            0b0000111111111000, # type_mask (only positions enabled)
            north, east, down, # x, y, z positions (or North, East, Down in the MAV_FRAME_BODY_NED frame
            0, 0, 0, # x, y, z velocity in m/s  (not used)
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
        # send command to vehicle
        inVehicle.send_mavlink(msg)
    else:    
        outputObj["name"]="gotoRelativeHome"
        outputObj["status"]="error"
        outputObj["error"]="Vehicle not armed"
    return outputObj


def gotoAbsolute(inVehicle, inLocation):        
    outputObj={}
    if inVehicle.armed:
        outputObj["name"]="gotoAbsolute"
        outputObj["status"]="success"
        print " Goto Location: %s" % inLocation     
        output = {"global_frame":inLocation}
        print "lat" + str(inLocation['lat'])
        #vehicle.mode = VehicleMode("GUIDED")
        inVehicle.simple_goto(LocationGlobal(inLocation['lat'],inLocation['lon'],inLocation['alt']), groundspeed=10)
    else:    
        outputObj["name"]="gotoAbsolute"
        outputObj["status"]="error"
        outputObj["error"]="Vehicle not armed"
    return outputObj

def roi(inVehicle, inLocation):        
    outputObj={}
    outputObj["name"]="roi"
    outputObj["status"]="success"
    print " Home Location: %s" % inLocation     
    output = {"home_location":inLocation}
    print "lat" + str(inLocation['lat'])
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

def getVehicleStatus(inVehicle):
    # inVehicle is an instance of the Vehicle class
    outputObj={}
    web.header('Content-Type', 'application/json')
    print ""
    print "###################################################################################"
    print "Autopilot Firmware version: %s" % inVehicle.version
    outputObj["version"]=str(inVehicle.version)
    print "Global Location: %s" % inVehicle.location.global_frame
    global_frame=latLonAltObj(inVehicle.location.global_frame)
    outputObj["global_frame"]=global_frame
    print "Global Location (relative altitude): %s" % inVehicle.location.global_relative_frame
    global_relative_frame=latLonAltObj(inVehicle.location.global_relative_frame)
    outputObj["global_relative_frame"]=global_relative_frame
    print "Local Location: %s" % inVehicle.location.local_frame    #NED
    local_frame={}
    local_frame["north"]=(inVehicle.location.local_frame.north)
    local_frame["east"]=(inVehicle.location.local_frame.east)
    local_frame["down"]=(inVehicle.location.local_frame.down)
    outputObj["local_frame"]=local_frame
    print "Attitude: %s" % inVehicle.attitude
    outputObj["attitude"]={"pitch":inVehicle.attitude.pitch,"roll":inVehicle.attitude.roll,"yaw":inVehicle.attitude.yaw}
    print "Velocity: %s" % inVehicle.velocity
    outputObj["velocity"]=(inVehicle.velocity)
    print "GPS: %s" % inVehicle.gps_0
    outputObj["gps_0"]={"eph":(inVehicle.gps_0.eph),"epv":(inVehicle.gps_0.eph),"fix_type":(inVehicle.gps_0.fix_type),"satellites_visible":(inVehicle.gps_0.satellites_visible)}
    print "Groundspeed: %s" % inVehicle.groundspeed
    outputObj["groundspeed"]=(inVehicle.groundspeed)
    print "Airspeed: %s" % inVehicle.airspeed
    outputObj["airspeed"]=(inVehicle.airspeed)
    print "Gimbal status: %s" % inVehicle.gimbal
    outputObj["gimbal"]={"pitch":inVehicle.gimbal.pitch,"roll":inVehicle.gimbal.roll,"yaw":inVehicle.gimbal.yaw}
    print "Battery: %s" % inVehicle.battery
    outputObj["battery"]={"voltage":inVehicle.battery.voltage,"current":inVehicle.battery.current,"level":inVehicle.battery.level}
    print "EKF OK?: %s" % inVehicle.ekf_ok
    outputObj["ekf_ok"]=(inVehicle.ekf_ok)
    print "Last Heartbeat: %s" % inVehicle.last_heartbeat
    outputObj["last_heartbeat"]=(inVehicle.last_heartbeat)
    print "Rangefinder: %s" % inVehicle.rangefinder
    outputObj["rangefinder"]={"distance":inVehicle.rangefinder.distance,"voltage":inVehicle.rangefinder.voltage}
    print "Heading: %s" % inVehicle.heading
    outputObj["heading"]=(inVehicle.heading)
    print "Is Armable?: %s" % inVehicle.is_armable
    outputObj["is_armable"]=(inVehicle.is_armable)
    print "System status: %s" % inVehicle.system_status.state
    outputObj["system_status"]=str(inVehicle.system_status.state)
    print "Mode: %s" % inVehicle.mode.name    # settable
    outputObj["mode"]=str(inVehicle.mode.name)
    print "Armed: %s" % inVehicle.armed    # settable    
    outputObj["armed"]=(inVehicle.armed)
    print "###################################################################################"
    print ""
    return outputObj

class index:        
    def GET(self):
        print "#####################################################################"
        print "Method GET of index"
        print "#####################################################################"
        applyHeadders()
        outputObj={}
        outputObj['_links']={
            'self':{"href": homeDomain},
            'vehicle': {
                'operations':  [
                    {"method":"GET",
                    "description":"Return the collection of available vehicles."},
                    {"method":"POST",
                    "description":"Add a connection to a new vehicle. It will return the id of the vehicle.",
                    "samplePayload":{"connection":"udp:10.0.0.2:6000"}}],
                    "href": homeDomain+"/vehicle" }}
        outputObj['id']="EntryPoint"
        output=json.dumps(outputObj)    
        return output

class vehicleIndex:        
    def GET(self):
        print "#####################################################################"
        print "Method GET of vehicleIndex"
        print "#####################################################################"
        applyHeadders()
        outputObj=[]
        for i in range (1,len(connectionStringArray)) :
            outputObj.append( {"id":i,
                    "details":{"method":"GET","href":homeDomain+"/vehicle/"+str(i)+"/","description":"Get status for vehicle " + str(i),"connection":connectionStringArray[i]}})
        output=json.dumps(outputObj)    
        return output

    def POST(self):
        print "#####################################################################"
        print "Method POST of vehicleIndex"
        print "#####################################################################"
        web.header('Content-Type', 'application/json')
        data = json.loads(web.data())
        connection = data["connection"]
        print connection
        connectionStringArray.append(connection)
        outputObj={}
        outputObj["connection"]=connection
        outputObj["id"]=len(connectionStringArray)-1
        return json.dumps(outputObj)

class action:     
    def OPTIONS(self, vehicleId):
        print "#####################################################################"
        print "Method OPTIONS of action - just here to suppor the CORS Cross-Origin security"
        print "#####################################################################"
        applyHeadders()

        outputObj={}
        output=json.dumps(outputObj)   
        return output


    def GET(self, vehicleId):
        print "#####################################################################"
        print "Method GET of action"
        print "#####################################################################"

        applyHeadders()
        inVehicle=connectVehicle(vehicleId)      
        vehicleStatus=getVehicleStatus(inVehicle)
        outputObj={}
        availableActions=[]
        #available when armed
        if vehicleStatus["armed"]:
            availableActions.append({   
                "name":"roi",
                "description":"Set a Region of Interest : When the drone is flying, it will face the point  <lat>,<lon>,<alt> (defaults to the home location)",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"roi","lat":51.3946,"lon":-1.299,"alt":105}
            })
            availableActions.append({   
                "name":"land",
                "description":"Land at current location",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"land"}
            })
            availableActions.append({   
                "name":"rtl",
                "description":"Return to launch: Return to the home location and land.",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"rtl"}
            })
            availableActions.append({   
                "name":"auto",
                "description":"Begin the pre-defined mission.",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"auto"}
            })
            availableActions.append({   
                "name":"gotoAbsolute",
                "description":"Go to the location at latitude <lat>, longitude <lon> and altitude <alt> (above sea level).",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"gotoAbsolute","lat":51.3946,"lon":-1.299,"alt":105} 
            })
            availableActions.append({   
                "name":"gotoRelativeHome",
                "description":"Go to the location <north> meters North, <east> meters East and <up> meters vertically from the home location.",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"gotoRelativeHome","north":30,"east":30,"up":10}
            })
            availableActions.append({   
                "name":"gotoRelativeCurrent",
                "description":"Go to the location <north> meters North, <east> meters East and <up> meters vertically from the current location.",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"gotoRelativeCurrent","north":30,"east":30,"up":10}
            })
        else :
            availableActions.append({   
                "name":"takeoff",
                "description":"Arm and takeoff in GUIDED mode to height of <height> (default 20m).",
                "href":homeDomain+"/vehicle/"+str(vehicleId)+"/action",
                "method":"POST",
                "samplePayload":{"name":"takeoff","height":30}
            })
        outputObj['availableActions']=availableActions
        output=json.dumps(outputObj)   
        return output

    def POST(self, vehicleId):
        print "#####################################################################"
        print "Method POST of action"
        print "#####################################################################"
        inVehicle=connectVehicle(vehicleId)      
        applyHeadders()
        data = json.loads(web.data())
        value = data["name"]
        print value
        outputObj={}
        if value=="rtl":
            outputObj["action"]=rtl(inVehicle)
        if value=="takeoff":
            height=data.get("height",20) #get height - default to 20
            print "Taking off to height of " + str(height)
            outputObj["action"]=takeoff(inVehicle,height)
        if value=="auto":
            outputObj["action"]=auto(inVehicle)
        if value=="land":
            outputObj["action"]=land(inVehicle)
        if value=="gotoAbsolute":
            defaultLocation=inVehicle.location.global_frame #default to current position
            print "Global Frame" + str(defaultLocation)
            inLat=data.get("lat",defaultLocation.lat)
            inLon=data.get("lon",defaultLocation.lon)
            inAlt=data.get("alt",defaultLocation.alt)
            locationObj={'lat':float(inLat), 'lon':float(inLon), 'alt':float(inAlt)}
            outputObj["action"]=gotoAbsolute(inVehicle,locationObj)
        if value=="gotoRelativeHome":
            inNorth=data.get("north",0)
            inEast=data.get("east",0)
            inDown=-data.get("up",0)
            outputObj["action"]=gotoRelative(inVehicle,inNorth,inEast,inDown)
        if value=="gotoRelativeCurrent":
            inNorth=data.get("north",0)
            inEast=data.get("east",0)
            inDown=-data.get("up",0)
            outputObj["action"]=goto(inVehicle,inNorth,inEast,inDown)
        if value=="roi":
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            defaultLocation=inVehicle.home_location
            inLat=data.get("lat",defaultLocation.lat)
            inLon=data.get("lon",defaultLocation.lon)
            inAlt=data.get("alt",defaultLocation.alt)
            locationObj={'lat':float(inLat), 'lon':float(inLon), 'alt':float(inAlt)}
            outputObj["action"]=roi(inVehicle,locationObj)
        return json.dumps(outputObj)

class missionCommands:        
    def GET(self, vehicleId):
        print "#####################################################################"
        print "Method GET of missionCommands "
        print "#####################################################################"
        print "vehicleId = '"+vehicleId+"'"
        applyHeadders()
        inVehicle=connectVehicle(vehicleId)      
        vehicleStatus=getVehicleStatus(inVehicle)
        outputObj={}
        availableActions=[]
        cmds = inVehicle.commands
        cmds.download()
        cmds.wait_ready()
        print "#####################################################################"
        print "#####################################################################"
        print "Mission Commands"
        # Save the vehicle commands to a list
        missionlist=[]
        for cmd in cmds:
            autoContinue=True
            if (cmd.autocontinue==0):
                autoContinue=False
            missionlist.append({'id':cmd.seq,"autoContinue": autoContinue ,"command": cmd.command,"coordinate": [cmd.x,cmd.y,cmd.z],'frame':cmd.frame,'param1':cmd.param1,'param2':cmd.param2,'param3':cmd.param3,'param4':cmd.param4,"type": "missionItem"})
            print cmd
        print missionlist
        outputObj['items']=missionlist
        outputObj['plannedHomePosition']={'id':0,'autoContinue':True,'command':16,"coordinate": [inVehicle.home_location.lat,inVehicle.home_location.lon,0], 'frame':0,'param1':0,'param2':0,'param3':0,'param4':0,'type':'missionItem'}
        outputObj['version']='1.0'
        outputObj['MAV_AUTOPILOT']=3
        outputObj['complexItems']=[]
        outputObj['groundStation']='QGroundControl'



        #outputObj['missionCommands']=cmds
        output=json.dumps(outputObj)   
        return output

class vehicleStatus:        
    def GET(self, vehicleId, statusVal):
        print "#####################################################################"
        print "Method GET of vehicleStatus "
        print "#####################################################################"
        print "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'"
        applyHeadders()
        outputObj={}
        #test if vehicleId is an integer 1-4
        try:
            vehId=int(vehicleId)
        except ValueError:
            stringArray=vehicleId.split('/')
            vehicleId=stringArray[0]
            statusVal=stringArray[1]
        print "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'"
        inVehicle=connectVehicle(vehicleId)      
        vehicleStatus=getVehicleStatus(inVehicle)
        outputObj['homeLocation']={"method":"GET","href":homeDomain + "/vehicle/" + str(vehicleId) + "/homelocation","description":"Get the home location for this vehicle"}
        outputObj['availableActions']={"method":"GET","href":homeDomain+ "/vehicle/" + str(vehicleId) +"/action","description":"Get the actions available for this vehicle."}
        outputObj['missionCommands']={"method":"GET","href":homeDomain+ "/vehicle/" + str(vehicleId) +"/missionCommands","description":"Get the current mission commands from the vehicle."}
        output=""
        if statusVal=="/":
            statusVal=""            
        if statusVal=="":
            outputObj["vehicleStatus"]=vehicleStatus
            output = json.dumps(outputObj)
        elif statusVal=="homelocation":
            cmds = inVehicle.commands
            cmds.download()
            cmds.wait_ready()
            print " Home Location: %s" % inVehicle.home_location     
            output = json.dumps({"home_location":latLonAltObj(inVehicle.home_location)}   )   
        elif statusVal=="action":
            outputObj["vehicleStatus"]={"error":"Use "+homeDomain+"/vehicle/1/action  (with no / at the end)."}
            output = json.dumps(outputObj)
        else:
            statusLen=len(statusVal)
            print statusLen
            #statusVal=statusVal[1:]
            print statusVal
            outputObj["vehicleStatus"]={statusVal: vehicleStatus.get(statusVal,{"error":"Vehicle status '"+statusVal+"' not found. Try getting all using "+homeDomain+"/vehicle/"+vehicleId+"/"})}
            output = json.dumps(outputObj)
        return output

class catchAll:
    def GET(self, user):
        print "#####################################################################"
        print "Method GET of catchAll"
        print "#####################################################################"
        applyHeadders()
        print homeDomain
        outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/1/ for the status of vehicle #1 or to "+homeDomain+"/vehicle/1/action for the list of actions available for vehicle #1." }
        return json.dumps(outputObj)

    def POST(self, user):
        print "#####################################################################"
        print "Method POST of catchAll"
        print "#####################################################################"
        applyHeadders()
        outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/1/ for the status of vehicle #1 or to "+homeDomain+"/vehicle/1/action for the list of actions available for vehicle #1." }
        return json.dumps(outputObj)


urls = (
    '/', 'index',
    '/vehicle/(.*)/action', 'action',
    '/vehicle/(.*)/missionCommands', 'missionCommands',
    '/vehicle', 'vehicleIndex',
    '/vehicle/(.*)/(.*)', 'vehicleStatus',
    '/(.*)', 'catchAll'
)

homeDomain='http://sail.vodafone.com/drone'

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()






