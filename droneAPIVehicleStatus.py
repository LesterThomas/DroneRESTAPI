#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math, docker
import  droneAPIUtils





class vehicleStatus:        
    def GET(self, vehicleId):
        try:
            droneAPIUtils.my_logger.info( "#### Method GET of vehicleStatus ####")
            statusVal=''  #removed statusVal which used to have the fields) from the URL because of the trailing / issue
            droneAPIUtils.my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            droneAPIUtils.applyHeadders()
            outputObj={}

            actions=[{"method":"DELETE","href":droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId),"title":"Delete connection to vehicle " + str(vehicleId)}]

            #test if vehicleId is an integer 1-4
            #try:
            #    vehId=int(vehicleId)
            #except ValueError:
            #    stringArray=vehicleId.split('/')
            #    vehicleId=stringArray[0]
            #    statusVal=stringArray[1]
            #droneAPIUtils.my_logger.debug( "vehicleId = '"+vehicleId+"', statusVal = '"+statusVal+"'")
            try:
                inVehicle=droneAPIUtils.connectVehicle(vehicleId)   
            except Warning:
                droneAPIUtils.my_logger.warn("vehicleStatus:GET Cant connect to vehicle - vehicle starting up" + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle - vehicle starting up ", "_actions": actions}) 
            except Exception:
                droneAPIUtils.my_logger.warn("vehicleStatus:GET Cant connect to vehicle" + str(vehicleId))
                jsonObjStr=droneAPIUtils.redisdB.get('connectionString:' + str(vehicleId))
                return json.dumps({"error":"Cant connect to vehicle " + str(vehicleId) + "with connection " + jsonObjStr, "_actions": actions}) 
            vehicleStatus=droneAPIUtils.getVehicleStatus(inVehicle)
            vehicleStatus["name"]=droneAPIUtils.connectionNameTypeDict[vehicleId]['name']
            vehicleStatus["vehicleType"]=droneAPIUtils.connectionNameTypeDict[vehicleId]['vehicleType']

            vehicleStatus["zone"]=droneAPIUtils.authorizedZoneDict.get(vehicleId)
            if not vehicleStatus["zone"]: #if no authorizedZone then set default
                vehicleStatus["zone"]={"shape":{"name":"circle","lat":vehicleStatus["global_frame"]["lat"],"lon":vehicleStatus["global_frame"]["lon"],"radius":500}}


            #check if vehicle still in zone
            distance=droneAPIUtils.distanceInMeters(vehicleStatus["zone"]["shape"]["lat"],vehicleStatus["zone"]["shape"]["lon"],vehicleStatus["global_frame"]["lat"],vehicleStatus["global_frame"]["lon"])
            if (distance>500):
                rtl(inVehicle)


            vehicleStatus['id']=vehicleId
            vehicleStatus['_links']={};
            vehicleStatus['_links']["self"]={"href": droneAPIUtils.homeDomain+"/vehicle/"+str(vehicleId), "title":"Get status for vehicle "+str(vehicleId)+"."}
            vehicleStatus['_links']['homeLocation']={"href":droneAPIUtils.homeDomain + "/vehicle/" + str(vehicleId) + "/homeLocation","title":"Get the home location for this vehicle"}
            vehicleStatus['_links']['action']={"href":droneAPIUtils.homeDomain+ "/vehicle/" + str(vehicleId) +"/action","title":"Get the actions  for this vehicle."}
            vehicleStatus['_links']['mission']={"href":droneAPIUtils.homeDomain+ "/vehicle/" + str(vehicleId) +"/mission","title":"Get the current mission commands from the vehicle."}
            vehicleStatus['_links']['simulator']={"href":droneAPIUtils.homeDomain+ "/vehicle/" + str(vehicleId) +"/simulator","title":"Get the current simulator parameters from the vehicle."}
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
                droneAPIUtils.my_logger.debug( " Home Location: %s" % inVehicle.home_location     )
                output = json.dumps({"home_location":droneAPIUtils.latLonAltObj(inVehicle.home_location)}   )   
            elif statusVal=="action":
                outputObj={"error":"Use "+droneAPIUtils.homeDomain+"/vehicle/1/action  (with no / at the end)."}
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
            else:
                statusLen=len(statusVal)
                droneAPIUtils.my_logger.debug( statusLen)
                #statusVal=statusVal[1:]
                droneAPIUtils.my_logger.debug( statusVal)
                outputObj={statusVal: vehicleStatus.get(statusVal,{"error":"Vehicle status '"+statusVal+"' not found. Try getting all using "+droneAPIUtils.homeDomain+"/vehicle/"+vehicleId+"/"})}
                outputObj["_actions"]=actions
                output = json.dumps(outputObj)
        except Exception as e: 
            droneAPIUtils.my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def DELETE(self, vehicleId):
        try:
            droneAPIUtils.my_logger.info( "#### Method DELETE of vehicleStatus ####")
            #delete docker container for this vehicle
            jsonObjStr=droneAPIUtils.redisdB.get('connectionString:' + str(vehicleId))
            droneAPIUtils.my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
            jsonObj=json.loads(jsonObjStr)
            connectionString=jsonObj['connectionString']

            droneAPIUtils.redisdB.delete("connectionString:"+vehicleId)
            droneAPIUtils.connectionDict.pop("connectionString:"+vehicleId, None)
            dockerHostsArray=json.loads(droneAPIUtils.redisdB.get("dockerHostsArray"))


            ipAddress=connectionString[4:-6]
            connectionStringLength=len(connectionString)
            droneAPIUtils.my_logger.info( "connectionStringLength="+ str(connectionStringLength))
            port=connectionString[connectionStringLength-5:]
            index=-1
            for port in dockerHostsArray[0]['usedPorts']:
                index=index+1
                if (dockerHostsArray[0]['usedPorts'][index]==int(port)):
                    dockerHostsArray[0]['usedPorts'].pop(index)

            droneAPIUtils.redisdB.set("dockerHostsArray",json.dumps(dockerHostsArray))

            dockerContainerId=jsonObj['dockerContainerId']
            droneAPIUtils.my_logger.info( "Deleting container")
            droneAPIUtils.my_logger.info( "dockerHost = '"+ipAddress+"'")
            droneAPIUtils.my_logger.info( "port = '"+str(port)+"'")
            droneAPIUtils.my_logger.info( "containerId = '"+dockerContainerId+"'")
            dockerClient = docker.DockerClient(version='1.27',base_url='tcp://'+ipAddress+':4243') #docker.from_env(version='1.27') 
            container=dockerClient.containers.get(dockerContainerId)
            container.stop()
            dockerClient.containers.prune(filters=None)

            outputObj={"status":"success"}
            output = json.dumps(outputObj)
        except Exception as e: 
            droneAPIUtils.my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def OPTIONS(self,vehicleId):
        try:
            droneAPIUtils.my_logger.info( "#### OPTIONS of vehicleStatus - just here to suppor the CORS Cross-Origin security #####")
            droneAPIUtils.applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            droneAPIUtils.my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output
       
    def terminateCloudInstance(vehicleId):
        jsonObjStr=droneAPIUtils.redisdB.get('connectionString:' + str(vehicleId))
        droneAPIUtils.my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
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
                            #droneAPIUtils.my_logger.debug(instance)
                            droneAPIUtils.my_logger.debug(instance["PrivateIpAddress"],instance["InstanceId"],instance["InstanceType"],instance["State"]["Name"])
                            instances.append(instance["InstanceId"])
                        
            droneAPIUtils.my_logger.debug("instances to terminate")
            droneAPIUtils.my_logger.debug(instances)

            if (len(instances)>0):  
                #startresp=ec2client.start_instances(InstanceIds=["i-094270016448e61e2"])
                stopresp=ec2client.terminate_instances(InstanceIds=instances)
                droneAPIUtils.my_logger.debug("Terminated instance")

        except Exception as inst:
            droneAPIUtils.my_logger.error( "Error conneting to AWS:")
            droneAPIUtils.my_logger.error( "VehicleId=")
            droneAPIUtils.my_logger.error( vehicleId)
            droneAPIUtils.my_logger.error( "Exception=")
            droneAPIUtils.my_logger.error( inst)
            #ignore error and continue
        
        return
