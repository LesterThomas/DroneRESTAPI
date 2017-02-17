FROM ubuntu:14.04

RUN apt-get update -y
RUN apt-get upgrade -y 
RUN apt-get update -y
RUN apt-get install -y python-matplotlib 
RUN apt-get update -y
RUN apt-get install -y python-serial
RUN apt-get update -y
RUN apt-get update -y
RUN apt-get install -y python-lxml
RUN apt-get update -y
RUN apt-get install -y python-scipy 
RUN apt-get update -y
RUN apt-get install -y python-opencv 
RUN apt-get update -y
RUN apt-get install -y ccache 
RUN apt-get update -y
RUN apt-get install -y gawk 
RUN apt-get update -y
RUN apt-get install -y git 
RUN apt-get update -y
RUN apt-get install -y python-pip
RUN apt-get update -y
#RUN pip install --update pip
RUN apt-get install -y python-pexpect
RUN apt-get update -y
RUN pip install future pymavlink MAVProxy
COPY ardupilot /arducopter/



RUN echo 'export PATH=$PATH:/jsbsim/src' >> ~/.bashrc
RUN echo 'export PATH=$PATH:/ardupilot/Tools/autotest' >> ~/.bashrc
RUN echo 'export PATH=/usr/lib/ccache:$PATH' >> ~/.bashrc
RUN . ~/.bashrc
RUN echo 'NewburyEMH=51.4049426,-1.3049351,105,0' >> /arducopter/Tools/autotest/locations.txt 

RUN apt-get install -y python-pip
RUN apt-get install -y python-dev
RUN pip install dronekit
RUN pip install web.py
#RUN apt-get install wget -y
#RUN wget https://raw.githubusercontent.com/LesterThomas/DroneRESTAPI/master/rest.py
COPY rest.py /

RUN chmod -R 777 /arducopter
WORKDIR "/arducopter/ArduCopter"
#RUN python /arducopter/Tools/autotest/sim_vehicle.py -w -L NewburyEMH &

EXPOSE 1234
CMD python /rest.py 1234 | python /arducopter/Tools/autotest/sim_vehicle.py -N -w -L NewburyEMH  


