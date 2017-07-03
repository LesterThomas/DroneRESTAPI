FROM ubuntu:14.04

RUN apt-get update -y
RUN apt-get upgrade -y 
RUN apt-get install -y python-matplotlib 
RUN apt-get install -y python-serial
RUN apt-get install -y python-lxml
RUN apt-get install -y python-scipy 
RUN apt-get install -y python-opencv 
RUN apt-get install -y ccache 
RUN apt-get install -y gawk 
RUN apt-get install -y git 
RUN apt-get install -y python-pip
#RUN pip install --update pip
RUN apt-get install -y python-pexpect
RUN pip install future pymavlink MAVProxy
COPY ardupilot /arducopter/
RUN chmod -R 777 /arducopter
RUN echo 'export PATH=$PATH:/jsbsim/src' >> ~/.bashrc
RUN echo 'export PATH=$PATH:/Documents/ardupilot/Tools/autotest' >> ~/.bashrc
RUN echo 'export PATH=/usr/lib/ccache:$PATH' >> ~/.bashrc
RUN . ~/.bashrc
RUN echo 'NewburyEMH=51.4049426,-1.3049351,105,0' >> /arducopter/Tools/autotest/locations.txt 
RUN echo 'SOUTHAMPTON=50.905515,-1.428529,5,0' >> /arducopter/Tools/autotest/locations.txt 

RUN apt-get install -y python-pip
RUN apt-get install -y python-dev
RUN pip install dronekit
RUN pip install web.py


