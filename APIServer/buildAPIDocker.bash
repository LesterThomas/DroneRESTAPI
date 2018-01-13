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
#docker ps -a | awk '{ print $1,$2 }' | grep droneapiserver | awk '{print $1 }' | xargs -I {} docker kill {}
#docker ps -a | awk '{ print $1,$2 }' | grep droneapiserver | awk '{print $1 }' | xargs -I {} docker rm {}
docker build -t lesterthomas/droneapiserver:$VERSION .
#docker run -d  --link redis:redis -e "DRONEAPI_URL=http://test.droneapi.net" -e "DOCKER_HOST_IP=172.17.0.1" -e "VIRTUAL_HOST=test.droneapi.net"  lesterthomas/droneapiserver:$VERSION

