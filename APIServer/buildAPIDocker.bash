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
cp -r ../../droneConsole/app static
docker stop $(docker ps -a -q -f name=droneapiserver)
docker rm $(docker ps -a -q -f name=droneapiserver)
docker build -t lesterthomas/droneapiserver:$VERSION .
docker run -d -p 1235:1234 --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" --name droneapiserver lesterthomas/droneapiserver:$VERSION
echo "Container running. Showing log tail"
sleep 3
docker exec -t -i droneapiserver cat droneapi.log
docker exec -t -i droneapiserver tail -f droneapi.log