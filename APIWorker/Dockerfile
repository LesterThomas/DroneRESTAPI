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
RUN apt-get install -y python-pexpect
RUN apt-get install -y python-pip
RUN apt-get install -y python-dev
RUN pip install dronekit
RUN pip install web.py
RUN pip install redis
RUN pip install --upgrade requests
RUN pip install boto3
RUN pip install docker
RUN pip install watchtower
RUN pip install psutil
RUN pip install kubernetes
RUN pip install pyyaml

RUN apt-get install -y awscli
COPY *.py /
EXPOSE 1236
CMD python /droneAPIMain.py 1236

