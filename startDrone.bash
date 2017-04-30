 #!/bin/bash

 #sleep 15
 sleep $1
 let PORT=14551+$1*10
 echo $PORT
 connectionString='{"vehicleType":"real","connectionString":"udp:127.0.0.1:'$PORT'"}' 
 echo $connectionString
 sleep 1
 echo ""
 curl --data $connectionString -X POST http://localhost:1235/vehicle
 sleep 1

 #bash ./droneRegisterZone.bash $1 &
 
 LOC='ENBOURNE'$1
 echo $LOC
 cd ~/Documents/ardupilot/ArduCopter
 sim_vehicle.py -L $LOC --instance=$1

 sleep 50



