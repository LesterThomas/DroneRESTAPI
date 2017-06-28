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

docker stop $(docker ps -a -q -f name=droneapi)
docker rm $(docker ps -a -q -f name=droneapi)
docker build -f APIDockerBuild/Dockerfile -t lesterthomas/droneapi:$VERSION .
docker run -d -p 1235:1234 --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" --name droneapi lesterthomas/droneapi:$VERSION 
echo "Container running. Showing log tail"
sleep 3
docker exec -t -i droneapi cat droneapi.log
docker exec -t -i droneapi tail -f droneapi.log