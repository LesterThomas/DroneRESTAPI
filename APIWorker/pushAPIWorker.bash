#!/bin/bash
echo "**************************************************************************************************************"
echo "Running APIWorker bash script"
echo "**************************************************************************************************************"

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

echo "Running locally"
docker ps -a | awk '{ print $1,$2 }' | grep droneapiworker | awk '{print $1 }' | xargs -I {} docker stop {}
docker ps -a | awk '{ print $1,$2 }' | grep droneapiworker | awk '{print $1 }' | xargs -I {} docker rm {}

echo "Applying Python Code styling"
autopep8 -a -a -v -i --max-line-length 140 *.py

echo "Generating Python pdoc documentation"
pdoc --html --overwrite droneAPICommand.py
pdoc --html --overwrite droneAPIHomeLocation.py
pdoc --html --overwrite droneAPISimulator.py
pdoc --html --overwrite droneAPIVehicleStatus.py
pdoc --html --overwrite droneAPIAdmin.py
pdoc --html --overwrite droneAPIMain.py
pdoc --html --overwrite droneAPIUtils.py
pdoc --html --overwrite droneAPIAuthorizedZone.py
pdoc --html --overwrite droneAPIMission.py
pdoc --html --overwrite droneAPIVehicleIndex.py


docker build -t lesterthomas/droneapiworker:$VERSION .
docker run -d -p 8000:1234 --link redis:redis -e "DRONEAPI_URL=http://test.droneapi.net" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7"  -e "DOCKER_WORKER_IMAGE=lesterthomas/droneapiworker:$VERSION"  -e "DOCKER_SERVER_IMAGE=lesterthomas/droneapiserver:$VERSION" -e "WORKER_URL=192.168.1.67:8000"  lesterthomas/droneapiworker:$VERSION
