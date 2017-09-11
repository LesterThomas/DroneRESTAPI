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

docker ps -a | awk '{ print $1,$2 }' | grep droneapiworker | awk '{print $1 }' | xargs -I {} docker stop {}
docker ps -a | awk '{ print $1,$2 }' | grep droneapiworker | awk '{print $1 }' | xargs -I {} docker rm {}
docker build -t lesterthomas/droneapiworker:$VERSION .
docker run -d -p 8000:1234 --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" -e "WORKER_URL=192.168.1.67:8000" --name droneapiworker1 lesterthomas/droneapiworker:$VERSION

echo "Container running. Showing log tail"
sleep 3
docker exec -t -i droneapiworker1 cat droneapi.log
docker exec -t -i droneapiworker1 tail -f droneapi.log