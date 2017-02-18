FROM lesterthomas/sitlbase:1.0

COPY rest.py /
COPY static /
WORKDIR "/arducopter/ArduCopter"
EXPOSE 1234
CMD python /rest.py 1234 | python /arducopter/Tools/autotest/sim_vehicle.py -N -w -L NewburyEMH  
