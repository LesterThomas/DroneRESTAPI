#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math, uuid, docker, redis
import droneAPIMain, droneAPIUtils

my_logger = droneAPIMain.my_logger



class vehicleIndex:   



 


 
    def GET(self):
        try:
            my_logger.info( "#### Method GET of vehicleIndex #####")
            droneAPIUtils.applyHeadders()
            outputObj=[]

            keys=droneAPIMain.redisdB.keys("connectionString:*")
            for key in keys:
                my_logger.debug( "key = '"+key+"'")
                jsonObjStr=droneAPIMain.redisdB.get(key)
                my_logger.debug( "redisDbObj = '"+jsonObjStr+"'")
                jsonObj=json.loads(jsonObjStr)
                connectionString=jsonObj['connectionString']
                vehicleName=jsonObj['name']
                vehicleType=jsonObj['vehicleType']
                droneId=key[17:]

                outputObj.append( {"_links":{"self":{"href":droneAPIMain.homeDomain+"/vehicle/"+str(droneId),"title":"Get status for vehicle " + str(droneId)}},
                        "id":str(droneId),"name":vehicleName,"vehicleType":vehicleType})

            actions='[{"name":"Add vehicle",\n"method":"POST",\n"title":"Add a connection to a new vehicle. Type is real or simulated (conection string is automatic for simulated vehicle). The connectionString is <udp/tcp>:<ip>;<port> eg tcp:123.123.123.213:14550 It will return the id of the vehicle. ",\n"href": "' + droneAPIMain.homeDomain+ '/vehicle",\n"fields":[{"name":"vehicleType", "type":{"listOfValues":["simulated","real"]}}, {"name":"connectionString","type":"string"}, {"name":"name","type":"string"}] }]\n'
            self={"self":{"title":"Return the collection of available vehicles.","href": droneAPIMain.homeDomain+"/vehicle" }}
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
        try:
            my_logger.info( "#### Method POST of vehicleIndex #####")
            droneAPIUtils.applyHeadders()
            dataStr=web.data()
            my_logger.info( dataStr)            
            data = json.loads(dataStr)
            droneType=data["vehicleType"]
            vehicleName=data["name"]
            connection=None
            dockerContainerId="N/A"
            if (droneType=="simulated"):
                
                
                #build simulated drone via Docker
                #docker api available on host at
                #http://172.17.42.1:4243/containers/json
                #2 steps to to create a drone
                #curl -X POST -H "Content-Type: application/json" -d '{"Image": "lesterthomas/dronesim:1.7", "ExposedPorts": { "14550/tcp": {} }}' http://172.17.42.1:4243/containers/create
                #returns {"Id":"269c290ad5da6ad15b2d8ed44f5a8d59caba4333bfedbca9795b1c0fc716f6d4","Warnings":null}
                #2nd step
                #curl -X POST -H "Content-Type: application/json" -d '{"PortBindings": { "14550/tcp": [{ "HostPort": "14550" }] }}' http://172.17.42.1:4243/containers/7005495cc1b47884089e64cf7e6c9fe45112c1cf1e5be5f2514ac1342b415ee4/start


                #private_ip_address=this.launchCloudImage('ami-5be0f43f', 't2.micro', ['sg-fd0c8394'])            
                #connection="tcp:" + str(createresponse[0].private_ip_address) + ":14550"
                imageAndPort=self.getNextImageAndPort() 
                dockerClient = docker.from_env(version='1.27')
                dockerContainer=dockerClient.containers.run('lesterthomas/dronesim:1.7', detach=True, ports={'14550/tcp': imageAndPort['port']} )
                dockerContainerId=dockerContainer.id
                my_logger.info( "container Id=" + str(dockerContainerId))


                connection="tcp:"+imageAndPort['image']+":"+str(imageAndPort['port']) 

            else:
                connection = data["connectionString"]
            
            my_logger.debug( connection)

            uuidVal=uuid.uuid4()
            key=str(uuidVal)[:8]
            my_logger.info("adding connectionString to Redis db with key '"+"connectionString:"+str(key)+"'")
            droneAPIMain.redisdB.set("connectionString:"+key,json.dumps({"connectionString":connection,"name":vehicleName,"vehicleType":droneType,"startTime":time.time(),"dockerContainerId":dockerContainerId}))

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
                    
        my_logger.debug("Non terminated instances=")
        my_logger.debug(len(instances))
        if (len(instances)>20):
            outputObj={}
            outputObj["status"]="Error: can't launch more than "+str(20)+" cloud images"
            return json.dumps(outputObj)


        my_logger.info("Creating new AWS image")
        ec2resource = boto3.resource('ec2')
        createresponse=ec2resource.create_instances(ImageId=ImageId, MinCount=1, MaxCount=1,InstanceType=InstanceType,SecurityGroupIds=SecurityGroupIds)
        my_logger.info(createresponse[0].private_ip_address)
        return private_ip_address

    #get the next image and port to launch dronesim docker image (create new image if necessary)
    def getNextImageAndPort(self):
        firstFreePort=0
        my_logger.info("dockerHostsArray")
        keys=droneAPIMain.redisdB.keys("dockerHostsArray")
        dockerHostsArray=json.loads(droneAPIMain.redisdB.get(keys[0]))
        my_logger.info(dockerHostsArray)

        #initially always use current image
        for i in range(14550,14560):
            #find first unused port
            portList=dockerHostsArray[0]['usedPorts'] # [{"internalIP":"localhost","usedPorts":[]}]
            if not(i in portList):
                firstFreePort=i
                break
        dockerHostsArray[0]['usedPorts'].append(i)
        my_logger.info("First unassigned port:"+ str(firstFreePort))

        droneAPIMain.redisdB.set("dockerHostsArray",json.dumps(dockerHostsArray))
        return {"image":"localhost","port":firstFreePort}



