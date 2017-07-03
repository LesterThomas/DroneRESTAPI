docker run -d -t -i -p 14560:14550 lesterthomas/dronesim:1.7 /usr/bin/python /arducopter/Tools/autotest/sim_vehicle.py -N -w --out=tcpin:0.0.0.0:14550 --custom-location 51.3955,-1.5342,105,0
