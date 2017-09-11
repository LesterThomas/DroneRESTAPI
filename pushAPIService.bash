#!/bin/bash


cd APIServer
source "pushAPIService.bash"


cd ../APIWorker
source "pushAPIWorker.bash"

cd ..


echo "Committing to GitHub"

git add .
git commit -m "$1"
git push



cd APIServer
source "postPushAPIService.bash"

cd ../APIWorker
source "postPushAPIService.bash"



echo "Triggering Postman tests via Jenkins"

curl "http://lesterthomas:Llandod1@localhost:8080/job/DroneAPI%20test/build?token=droneAPIToken&cause=$MAJOR_VERSION.$MINOR_VERSION"
