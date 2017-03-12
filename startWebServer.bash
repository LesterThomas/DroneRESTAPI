 #!/bin/bash
 cd ~/Documents/DroneRESTAPI/
 sleep  10
 curl -X GET  http://localhost:1235/vehicle/1/homelocation
 sleep 1
 curl --data '{"connection":"udp:127.0.0.1:14561"}' -X POST http://localhost:1235/vehicle
 sleep 1
 curl -X GET  http://localhost:1235/vehicle/1/missionActions
 sleep 1
 curl -X POST -d @sampleMission.json http://localhost:1235/vehicle/1/missionActions
 sleep 1


 cd ~/Documents/droneConsole
 grunt serve


