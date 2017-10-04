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

docker ps -a | awk '{ print $1,$2 }' | grep dockerperf | awk '{print $1 }' | xargs -I {} docker kill {}
docker ps -a | awk '{ print $1,$2 }' | grep dockerperf | awk '{print $1 }' | xargs -I {} docker rm {}
docker build -t lesterthomas/dockerperf:$VERSION .
docker run -d --restart=always -p 4000:1234  -e "DOCKER_HOST_IP=172.17.0.1"   lesterthomas/dockerperf:$VERSION


