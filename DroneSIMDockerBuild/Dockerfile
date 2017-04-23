FROM lesterthomas/sitlbase:1.0

WORKDIR "/arducopter/ArduCopter"
EXPOSE 14550
CMD sleep infinity | python /arducopter/Tools/autotest/sim_vehicle.py -N -w -L NewburyEMH  --out=tcpin:0.0.0.0:14550

