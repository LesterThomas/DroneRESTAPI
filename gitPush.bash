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

echo "Committing to GitHub"

git add .
git commit -m "v$VERSION $1"
git push 

echo "Running locally"

docker run -d -p 1235:1234 --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" --name droneapi lesterthomas/droneapi:$VERSION 
sleep 10

echo "Triggering Postman tests via Jenkins"

curl "localhost:8080/job/droneapi-test/build?token=PostmanLocal"

