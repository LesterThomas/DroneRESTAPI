#!/usr/bin/env python

# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException
# Import external modules
from collections import OrderedDict
import time, json, math, warnings, os, web, logging, logging.handlers, redis, uuid, time, boto3, traceback

my_logger = logging.getLogger('MyLogger')

# Import  modules that are part of this app
import droneAPISimulator, droneAPIUtils



#Set logging framework
LOG_FILENAME = 'droneapi.log'
my_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=200000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
my_logger.addHandler(handler)
my_logger.propegate=False

my_logger.info("##################################################################################")
my_logger.info("Starting DroneAPI server")
my_logger.info("##################################################################################")

versionDev=True#prod
defaultHomeDomain='' 
redisdB = None
if (versionDev):
    redisdB = redis.Redis(host='localhost', port=6379) #redis or localhost
    defaultHomeDomain='http://localhost:1235' #droneapi.ddns.net
    my_logger.info("Dev version connected to Redis at " + str(redisdB) + " and home domain of " + str(defaultHomeDomain))
else:
    my_logger.info("Prod version connected to Redis at " + str(redisdB) + " and home domain of " + str(defaultHomeDomain))
    defaultHomeDomain='http://droneapi.ddns.net:1235' 
    redisdB = redis.Redis(host='redis', port=6379) #redis or localhost

#test the redis dB
redisdB.set('foo', 'bar')
value = redisdB.get('foo')
if (value=='bar'):
    my_logger.info("Connected to Redis dB")
else:
    my_logger.error("Can not connect to Redis dB")
    raise Exception('Can not connect to Redis dB on port 6379')


connectionDict={} #holds a dictionary of DroneKit connection objects
connectionNameTypeDict={} #holds the additonal name, type and starttime for the conections
actionArrayDict={} #holds recent actions executied by each drone
authorizedZoneDict={} #holds zone authorizations for each drone
 




class index:        
    def GET(self):
        try:
            my_logger.info( "#### Method GET of index #####")
            droneAPIUtils.applyHeadders()
            outputObj={}
            outputObj['description']='Welcome to the Drone API homepage. WARNING: This API is experimental - use at your own discression. The API allows you to interact with simulated or real drones through a simple hypermedia REST API. There is a HAL API Browser at http://droneapi.ddns.net:1235/static/hal-browser/browser.html and a test client at http://droneapi.ddns.net:1235/static/app  The API is maintained at https://github.com/lesterthomas/DroneRESTAPI. This experimental API is part of the TM Forum Anything-as-a-Service Catalyst  https://projects.tmforum.org/wiki/display/PCT/A+Platform+for+IoT+and+Anything+as+a+Service+Catalyst '
            outputObj['_links']={
                'self':{"href": homeDomain, "title":"Home-page (or EntryPoint) of the API"},
                'vehicle': {
                        "title":"Return the collection of available vehicles.",
                        "href": homeDomain+"/vehicle" }
                        }
            output=json.dumps(outputObj)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             

        return output


class vehicleIndex:        
    def GET(self):
        try:
            global redisdB
            my_logger.info( "#### Method GET of vehicleIndex #####")
            droneAPIUtils.applyHeadders()
            outputObj=[]

            keys=redisdB.keys("connectionString:*")
            for key in keys:
                my_logger.debug( "key = '"+key+"'")
                jsonObjStr=redisdB.get(key)
                my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
                jsonObj=json.loads(jsonObjStr)
                connectionString=jsonObj['connectionString']
                vehicleName=jsonObj['name']
                vehicleType=jsonObj['vehicleType']
                droneId=key[17:]

                outputObj.append( {"_links":{"self":{"href":homeDomain+"/vehicle/"+str(droneId),"title":"Get status for vehicle " + str(droneId)}},
                        "id":str(droneId),"name":vehicleName,"vehicleType":vehicleType})

            actions='[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). The connectionString is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + homeDomain+ '/vehicle",\n"fields":[{"name":"vehicleType", "type":{"listOfValues":["simulated","real"]}}, {"name":"connectionString","type":"string"}, {"name":"name","type":"string"}] }]\n'
            self={"self":{"title":"Return the collection of available vehicles.","href": homeDomain+"/vehicle" }}
            my_logger.debug("actions")
            my_logger.debug(actions)
            jsonResponse='{"_embedded":{"vehicle":'+json.dumps(outputObj)+'},"_actions":'+actions+',"_links":'+ json.dumps(self)+'}'
            my_logger.debug("jsonResponse")
            my_logger.debug(jsonResponse)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
                            
        return jsonResponse

    def POST(self):
        global redisdB
        global config
        try:
            my_logger.info( "#### Method POST of vehicleIndex #####")
            droneAPIUtils.applyHeadders()
            dataStr=web.data()
            my_logger.info( dataStr)            
            data = json.loads(dataStr)
            droneType=data["vehicleType"]
            vehicleName=data["name"]
            connection=None
            if (droneType=="simulated"):
                #build simulted drone using aws

                #test how many non-terminated instances there are
                ec2client = boto3.client('ec2')
                response = ec2client.describe_instances()
                #print(response)
                instances=[]

                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        # This sample print will output entire Dictionary object
                        #print(instance)
                        # This will print will output the value of the Dictionary key 'InstanceId'
                        if (instance["State"]["Name"]!="terminated"):
                            instances.append(instance["InstanceId"])
                            
                my_logger.debug("Non terminated instances=")
                my_logger.debug(len(instances))
                if (len(instances)>20):
                    outputObj={}
                    outputObj["status"]="Error: can't launch more than "+str(20)+" drones"
                    return json.dumps(outputObj)


                my_logger.info("Creating new AWS image")
                ec2resource = boto3.resource('ec2')
                createresponse=ec2resource.create_instances(ImageId='ami-5be0f43f', MinCount=1, MaxCount=1,InstanceType='t2.micro',SecurityGroupIds=['sg-fd0c8394'])
                my_logger.info(createresponse[0].private_ip_address)
                connection="tcp:" + str(createresponse[0].private_ip_address) + ":14550"
            else:
                connection = data["connectionString"]
            
            my_logger.debug( connection)

            uuidVal=uuid.uuid4()
            key=str(uuidVal)[:8]
            my_logger.info("adding connectionString to Redis db with key '"+"connectionString:"+str(key)+"'")
            redisdB.set("connectionString:"+key,json.dumps({"connectionString":connection,"name":vehicleName,"vehicleType":droneType,"startTime":time.time()}))

            #connectionStringArray.append(connection)
            #connectionDict.append(None)
            #authorizedZoneDict.append({})
            outputObj={}
            outputObj["connection"]=connection
            outputObj["id"]=key
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)

    def OPTIONS(self):
        try:
            my_logger.info( "#### OPTIONS of vehicleIndex - just here to suppor the CORS Cross-Origin security #####")
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
        outputObj["_links"]={"self":{"href":homeDomain+"/vehicle/"+str(vehicleId)+"/mission","title":"Get the current mission commands from the vehicle."}}

        #outputObj['mission']=cmds
        output=json.dumps(outputObj)   
    except Exception as e: 
        my_logger.exception(e)
        tracebackStr = traceback.format_exc()
        traceLines = tracebackStr.split("\n")   
        return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
    return output

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
            outputObj={}
            outputObj["zone"]=zone
            authorizedZoneDict[vehicleId]=zone
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)





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
            output = json.dumps({"_links":{"self":{"href":homeDomain+"/vehicle/"+str(vehicleId)+"/homeLocation","title":"Get the home location for this vehicle"}},"home_location":droneAPIUtils.latLonAltObj(inVehicle.home_location)}   )   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output


class vehicleStatus:        
    def GET(self, vehicleId):
        try:
            my_logger.info( "#### Method GET of vehicleStatus ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            droneAPIUtils.applyHeadders()
            outputObj={}

            actions=[{"method":"DELETE","href":homeDomain+"/vehicle/"+str(vehicleId),"title":"Delete connection to vehicle " + str(vehicleId)}]

            #test if vehicleId is an integer 1-4
            #try:
            #    vehId=int(vehicleId)
            #except ValueError:
            #    stringArray=vehicleId.split('/')
            #    vehicleId=stringArray[0]
            #    statusVal=stringArray[1]
            #my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            try:
                inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
            except Warning:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up ", "_actions": actions}) 
            except Exception:
                my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                jsonObjStr=redisdB.get('connectionString:' + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId) + "with connection " + jsonObjStr, "_actions": actions}) 
            vehicleStatus=droneAPIUtils.getVehicleStatus(inVehicle)
            vehicleStatus["name"]=connectionNameTypeDict[vehicleId]['name']
            vehicleStatus["vehicleType"]=connectionNameTypeDict[vehicleId]['vehicleType']

            vehicleStatus["zone"]=authorizedZoneDict.get(vehicleId)
            if not vehicleStatus["zone"]: #if no authorizedZone then set default
                vehicleStatus["zone"]={"shape":{"name":"circle","lat":vehicleStatus["global_frame"]["lat"],"lon":vehicleStatus["global_frame"]["lon"]}}


            #check if vehicle still in zone
            distance=droneAPIUtils.distanceInMeters(vehicleStatus["zone"]["shape"]["lat"],vehicleStatus["zone"]["shape"]["lon"],vehicleStatus["global_frame"]["lat"],vehicleStatus["global_frame"]["lon"])
            if (distance>500):
                rtl(inVehicle)


            vehicleStatus['id']=vehicleId
            vehicleStatus['_links']={};
            vehicleStatus['_links']["self"]={"href": homeDomain+"/vehicle/"+str(vehicleId)+"/", "title":"Get status for vehicle "+str(vehicleId)+"."}
            vehicleStatus['_links']['homeLocation']={"href":homeDomain + "/vehicle/" + str(vehicleId) + "/homeLocation","title":"Get the home location for this vehicle"}
            vehicleStatus['_links']['action']={"href":homeDomain+ "/vehicle/" + str(vehicleId) +"/action","title":"Get the actions  for this vehicle."}
            vehicleStatus['_links']['mission']={"href":homeDomain+ "/vehicle/" + str(vehicleId) +"/mission","title":"Get the current mission commands from the vehicle."}
            vehicleStatus['_links']['simulator']={"href":homeDomain+ "/vehicle/" + str(vehicleId) +"/simulator","title":"Get the current simulator parameters from the vehicle."}
            output=""
            if statusVal=="/":
                statusVal=""            
            if statusVal=="":
                outputObj=vehicleStatus
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
            elif statusVal=="homelocation":
                cmds = inVehicle.commands
                cmds.download()
                cmds.wait_ready()
                my_logger.debug( " Home Location: %s" % inVehicle.home_location     )
                output = json.dumps({"home_location":droneAPIUtils.latLonAltObj(inVehicle.home_location)}   )   
            elif statusVal=="action":
                outputObj={"error":"Use "+homeDomain+"/vehicle/1/action  (with no / at the end)."}
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
            else:
                statusLen=len(statusVal)
                my_logger.debug( statusLen)
                #statusVal=statusVal[1:]
                my_logger.debug( statusVal)
                outputObj={statusVal: vehicleStatus.get(statusVal,{"error":"Vehicle status '"+statusVal+"' not found. Try getting all using "+homeDomain+"/vehicle/"+vehicleId+"/"})}
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def DELETE(self, vehicleId):
        try:
            my_logger.info( "#### Method DELETE of vehicleStatus ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            droneAPIUtils.applyHeadders()

            jsonObjStr=redisdB.get('connectionString:' + str(vehicleId))
            my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
            jsonObj=json.loads(jsonObjStr)
            connectionString=jsonObj['connectionString']
            ipAddress=connectionString[4:-6]


            try:
                #terminate any AWS instances with that private IP address
                ec2client = boto3.client('ec2')
                response = ec2client.describe_instances()
                #print(response)
                instances=[]

                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        # This sample print will output entire Dictionary object
                        #print(instance)
                        # This will print will output the value of the Dictionary key 'InstanceId'
                        if (instance["State"]["Name"]!="terminated"):
                            if (instance.get("PrivateIpAddress",None)==ipAddress):
                                #my_logger.debug(instance)
                                my_logger.debug(instance["PrivateIpAddress"],instance["InstanceId"],instance["InstanceType"],instance["State"]["Name"])
                                instances.append(instance["InstanceId"])
                            
                my_logger.debug("instances to terminate")
                my_logger.debug(instances)

                if (len(instances)>0):  
                    #startresp=ec2client.start_instances(InstanceIds=["i-094270016448e61e2"])
                    stopresp=ec2client.terminate_instances(InstanceIds=instances)
                    my_logger.debug("Terminated instance")

            except Exception as inst:
                my_logger.error( "Error conneting to AWS:")
                my_logger.error( "VehicleId=")
                my_logger.error( vehicleId)
                my_logger.error( "Exception=")
                my_logger.error( inst)
                #ignore error and continue


            my_logger.info("connectionString="+connectionString)
            my_logger.info("ipAddress="+ipAddress)
            redisdB.delete("connectionString:"+vehicleId)
            connectionDict.pop("connectionString:"+vehicleId, None)

            outputObj={"status":"success"}
            output = json.dumps(outputObj)
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self,vehicleId):
        try:
            my_logger.info( "#### OPTIONS of vehicleStatus - just here to suppor the CORS Cross-Origin security #####")
            droneAPIUtils.applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output
       


class catchAll:
    def GET(self, user):
        try:
            my_logger.info( "#### Method GET of catchAll ####")
            droneAPIUtils.applyHeadders()
            my_logger.debug( homeDomain)
            outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)

    def POST(self, user):
        try:
            my_logger.info( "#### Method POST of catchAll ####")
            droneAPIUtils.applyHeadders()
            outputObj={"Error":"No API endpoint found. Try navigating to "+homeDomain+"/vehicle for list of vehicles or to "+homeDomain+"/vehicle/<vehicleId> for the status of vehicle #1 or to "+homeDomain+"/vehicle/<vehicleId>/action for the list of actions available for vehicle <vehicleId>." }
        except Exception as e: 
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)


urls = (
    '/', 'index',
    '/vehicle/(.*)/action', 'droneAPIAction.action',
    '/vehicle/(.*)/homeLocation', 'homeLocation',
    '/vehicle/(.*)/mission', 'mission',
    '/vehicle/(.*)/authorizedZone', 'authorizedZone',
    '/vehicle/(.*)/simulator', 'droneAPISimulator.simulator',
    '/vehicle', 'vehicleIndex',
    '/vehicle/(.*)', 'vehicleStatus', #was     '/vehicle/(.*)/(.*)', 'vehicleStatus',
    '/(.*)', 'catchAll'
)

homeDomain = os.getenv('HOME_DOMAIN', defaultHomeDomain)
my_logger.debug( "Home Domain:"  + homeDomain)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()





