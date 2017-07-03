FROM lesterthomas/sitlbase:1.2

WORKDIR "/arducopter/ArduCopter"
EXPOSE 14550
CMD sleep infinity | python /arducopter/Tools/autotest/sim_vehicle.py -N -w --custom-location $LOCATION  --out=tcpin:0.0.0.0:14550

	