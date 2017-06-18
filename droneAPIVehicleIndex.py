#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math, uuid, docker, redis
import  droneAPIUtils




class vehicleIndex:   



 


 
    def GET(self):
        try:
            droneAPIUtils.my_logger.info( "#### Method GET of vehicleIndex #####")
            droneAPIUtils.applyHeadders()
            outputObj=[]

            keys=droneAPIUtils.redisdB.keys("connectionString:*")
            for key in keys:
                droneAPIUtils.my_logger.debug( "key = '"+key+"'")
                jsonObjStr=droneAPIUtils.redisdB.get(key)
                droneAPIUtils.my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
                jsonObj=json.loads(jsonObjStr)
                connectionString=jsonObj['connectionString']
                vehicleName=jsonObj['name']
                vehicleType=jsonObj['vehicleType']
                droneId=key[17:]

                outputObj.append( {"_links":{"self":{"href":droneAPIUtils.homeDomain+"/vehicle/"+str(droneId),"title":"Get status for vehicle " + str(droneId)}},
                        "id":str(droneId),"name":vehicleName,"vehicleType":vehicleType})

            actions='[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). The connectionString is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + droneAPIUtils.homeDomain+ '/vehicle",\n"fields":[{"name":"vehicleType", "type":{"listOfValues":["simulated","real"]}}, {"name":"connectionString","type":"string"}, {"name":"name","type":"string"}] }]\n'
            self={"self":{"title":"Return the collection of available vehicles.","href": droneAPIUtils.homeDomain+"/vehicle" }}
            droneAPIUtils.my_logger.debug("actions")
            droneAPIUtils.my_logger.debug(actions)
            jsonResponse='{"_embedded":{"vehicle":'+json.dumps(outputObj)+'},"_actions":'+actions+',"_links":'+ json.dumps(self)+'}'
            droneAPIUtils.my_logger.debug("jsonResponse")
            droneAPIUtils.my_logger.debug(jsonResponse)
        except Exception as e: 
            droneAPIUtils.my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
                            
        return jsonResponse

    def POST(self):
        try:
            droneAPIUtils.my_logger.info( "#### Method POST of vehicleIndex #####")
            droneAPIUtils.applyHeadders()
            dataStr=web.data()
            droneAPIUtils.my_logger.info( dataStr)            
            data = json.loads(dataStr)
            droneType=data["vehicleType"]
            vehicleName=data["name"]
            connection=None
            dockerContainerId="N/A"
            if (droneType=="simulated"):
                
                
                #build simulated drone via Docker
                #docker api available on host at
                #http://172.17.0.1:4243/containers/json

                #private_ip_address=this.launchCloudImage('ami-5be0f43f', 't2.micro', ['sg-fd0c8394'])            
                #connection="tcp:" + str(createresponse[0].private_ip_address) + ":14550"
                hostAndPort=self.getNexthostAndPort() 
                dockerClient = docker.DockerClient(version='1.27',base_url='tcp://'+hostAndPort['image']+':4243') #docker.from_env(version='1.27') 

                dockerContainer=dockerClient.containers.run('lesterthomas/dronesim:1.7', detach=True, ports={'14550/tcp': hostAndPort['port']} )
                dockerContainerId=dockerContainer.id
                droneAPIUtils.my_logger.info( "container Id=" + str(dockerContainerId))


                connection="tcp:"+hostAndPort['image']+":"+str(hostAndPort['port']) 

            else:
                connection = data["connectionString"]
            
            droneAPIUtils.my_logger.debug( connection)

            uuidVal=uuid.uuid4()
            key=str(uuidVal)[:8]
            droneAPIUtils.my_logger.info("adding connectionString to Redis db with key '"+"connectionString:"+str(key)+"'")
            droneAPIUtils.redisdB.set("connectionString:"+key,json.dumps({"connectionString":connection,"name":vehicleName,"vehicleType":droneType,"startTime":time.time(),"dockerContainerId":dockerContainerId}))

            outputObj={}
            outputObj["connection"]=connection
            outputObj["id"]=key
        except Exception as e: 
            droneAPIUtils.my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return json.dumps(outputObj)

    def OPTIONS(self):
        try:
            droneAPIUtils.my_logger.info( "#### OPTIONS of vehicleIndex - just here to suppor the CORS Cross-Origin security #####")
            droneAPIUtils.applyHeadders()

            outputObj={}
            output=json.dumps(outputObj)   
        except Exception as e: 
            droneAPIUtils.my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")   
            return json.dumps({"error":"An unknown Error occurred ","details":e.message, "args":e.args,"traceback":traceLines})             
        return output

    def launchCloudImage(ImageId, InstanceType, SecurityGroupIds):
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
                    
        droneAPIUtils.my_logger.debug("Non terminated instances=")
        droneAPIUtils.my_logger.debug(len(instances))
        if (len(instances)>20):
            outputObj={}
            outputObj["status"]="Error: can't launch more than "+str(20)+" cloud images"
            return json.dumps(outputObj)


        droneAPIUtils.my_logger.info("Creating new AWS image")
        ec2resource = boto3.resource('ec2')
        createresponse=ec2resource.create_instances(ImageId=ImageId, MinCount=1, MaxCount=1,InstanceType=InstanceType,SecurityGroupIds=SecurityGroupIds)
        droneAPIUtils.my_logger.info(createresponse[0].private_ip_address)
        return private_ip_address

    #get the next image and port to launch dronesim docker image (create new image if necessary)
    def getNexthostAndPort(self):
        firstFreePort=0
        keys=droneAPIUtils.redisdB.keys("dockerHostsArray")
        dockerHostsArray=json.loads(droneAPIUtils.redisdB.get(keys[0]))
        droneAPIUtils.my_logger.info("dockerHostsArray")
        droneAPIUtils.my_logger.info(dockerHostsArray)

        #initially always use current image
        for i in range(14550,14560):
            #find first unused port
            portList=dockerHostsArray[0]['usedPorts'] # [{"internalIP":"172.17.0.1","usedPorts":[]}]
            if not(i in portList):
                firstFreePort=i
                break
        dockerHostsArray[0]['usedPorts'].append(i)
        droneAPIUtils.my_logger.info("First unassigned port:"+ str(firstFreePort))

        droneAPIUtils.redisdB.set("dockerHostsArray",json.dumps(dockerHostsArray))
        return {"image":dockerHostsArray[0]['internalIP'],"port":firstFreePort}



