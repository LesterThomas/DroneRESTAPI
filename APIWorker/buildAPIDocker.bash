#!/bin/bash

#expects MAJOR_VERSION and MINOR_VERSION environment variables
MAJOR_VERSION=$(<"MajorVersion.txt" )
echo "MAJOR_VERSION"
echo "$MAJOR_VERSION"

MINOR_VERSION=$(<"MinorVersion.txt" )
echo "MINOR_VERSION"
echo $MINOR_VERSION

VERSION="$MAJOR_VERSION.$MINOR_VERSION"
echo "VERSION"
echo $VERSION

docker stop $(docker ps -a -q -f name=droneapiworker)
docker rm $(docker ps -a -q -f name=droneapiworker)
docker build -t lesterthomas/droneapiworker:$VERSION .
docker run -d -p 1236:1234 --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" -e "WORKER_URL=192.168.1.67:1236" --name droneapiworker lesterthomas/droneapiworker:$VERSION
echo "Container running. Showing log tail"
sleep 3
docker exec -t -i droneapiworker cat droneapi.log
docker exec -t -i droneapiworker tail -f droneapi.log