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

echo "Changing UI to point to prod api"
sed -i -e 's/192.168.1.67/droneapi.ddns.net/g' static/app/scripts/services/droneService.js
sed -i -e 's/192.168.1.67/droneapi.ddns.net/g' static/app/scripts/controllers/performanceController.js

echo "Running locally"
docker stop $(docker ps -a -q -f name=droneapiserver)
docker rm $(docker ps -a -q -f name=droneapiserver)

echo "Applying Python Code styling"
autopep8 -a -a -v -i --max-line-length 140 *.py

echo "Generating Python pdoc documentation"
pdoc --html --overwrite droneAPIAction.py
pdoc --html --overwrite droneAPIHomeLocation.py
pdoc --html --overwrite droneAPISimulator.py
pdoc --html --overwrite droneAPIVehicleStatus.py
pdoc --html --overwrite droneAPIAdmin.py
pdoc --html --overwrite droneAPIMain.py
pdoc --html --overwrite droneAPIUtils.py
pdoc --html --overwrite droneAPIAuthorizedZone.py
pdoc --html --overwrite droneAPIMission.py
pdoc --html --overwrite droneAPIVehicleIndex.py


docker build -t lesterthomas/droneapiserver:$VERSION .
docker run -p 1235:1234 -d --link redis:redis -e "DRONEAPI_URL=http://172.17.0.1:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" --name droneapiserver lesterthomas/droneapiserver:$VERSION
