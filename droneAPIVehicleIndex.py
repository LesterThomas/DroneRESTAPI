#This module has utility functions used by all the other modules in this App
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobal,LocationGlobalRelative, Command, mavutil, APIException

import web, logging, traceback, json, time, math, uuid
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
            droneAPIMain.redisdB.set("connectionString:"+key,json.dumps({"connectionString":connection,"name":vehicleName,"vehicleType":droneType,"startTime":time.time()}))

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

