#!/bin/bash
echo "**************************************************************************************************************"
echo "Running APIServer bash script"
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

echo "Changing UI to point to prod api and prod facebook id"
sed -i -e 's/192.168.1.67/droneapi.ddns.net/g' static/app/scripts/services/droneService.js
sed -i -e 's/192.168.1.67/droneapi.ddns.net/g' static/app/scripts/controllers/performanceController.js
sed -i -e 's/1988760538025932/136908103594406/g' static/app/scripts/app.js

echo "Running locally"
docker stop $(docker ps -a -q -f name=droneapiserver)
docker rm $(docker ps -a -q -f name=droneapiserver)

echo "Applying Python Code styling"
autopep8 -a -a -v -i --max-line-length 140 *.py

echo "Generating Python pdoc documentation"
pdoc --html --overwrite APIServerCommand.py
pdoc --html --overwrite APIServerHomeLocation.py
pdoc --html --overwrite APIServerSimulator.py
pdoc --html --overwrite APIServerVehicleStatus.py
pdoc --html --overwrite APIServerAdmin.py
pdoc --html --overwrite APIServerMain.py
pdoc --html --overwrite APIServerUtils.py
pdoc --html --overwrite APIServerAuthorizedZone.py
pdoc --html --overwrite APIServerMission.py
pdoc --html --overwrite APIServerVehicleIndex.py
pdoc --html --overwrite APIServerUser.py


docker build -t lesterthomas/droneapiserver:$VERSION .
docker run -p 1235:1234 -d --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" --name droneapiserver lesterthomas/droneapiserver:$VERSION
