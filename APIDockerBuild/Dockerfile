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

RUN apt-get install -y python-pip
RUN apt-get install -y python-dev
RUN pip install dronekit
RUN pip install web.py


COPY rest.py /
COPY static static/
RUN chmod -R 777 /static
EXPOSE 1234
CMD python /rest.py 1234 

