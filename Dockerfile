FROM lesterthomas/sitlbase:1.0

COPY rest.py /
COPY static /arducopter/ArduCopter/static/
RUN chmod -R 777 /arducopter/ArduCopter/static
WORKDIR "/arducopter/ArduCopter"
EXPOSE 1234 14550
CMD python /rest.py 1234 | python /arducopter/Tools/autotest/sim_vehicle.py -N -w -L NewburyEMH  --out=tcpin:0.0.0.0:14550

