 #!/bin/bash

 curl --data '{"connection":"udp:127.0.0.1:14561"}' -X POST http://localhost:1235/vehicle
 sleep 1

 cd ~/Documents/ardupilot/ArduCopter
 sim_vehicle.py -L ENBOURNE2 --instance=1


