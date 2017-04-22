 #!/bin/bash

 #sleep 15
 sleep $1
 let PORT=14551+$1*10
 echo $PORT
 connectionString='{"connection":"udp:127.0.0.1:'$PORT'"}'
 curl --data $connectionString -X POST http://localhost:1235/vehicle
 echo $connectionString
 sleep 1

 bash ./droneRegisterZone.bash $1 &
  LOC='ENBOURNE'$1
  echo $LOC
 cd ~/Documents/ardupilot/ArduCopter
 sim_vehicle.py -L $LOC --instance=$1

 sleep 50



