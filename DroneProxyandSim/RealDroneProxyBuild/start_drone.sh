#!/bin/bash

export APIKEY=$(curl -d '{"name":"Lester Thomas","email":"lesterthomas@hotmail.com","id":"10211950448669833","id_provider":"Facebook"}' -X POST 'http://droneapi.ddns.net/user' 2>/dev/null | python -c "import sys, json; print json.load(sys.stdin)['api_key']")

echo $APIKEY

echo "Creating connection to droneapi"

export DRONEAPIPORT=$(curl --header "apikey: $APIKEY" -d '{"name":"hackDrone","vehicle_type":"real"}' 'http://droneapi.ddns.net/vehicle' 2>/dev/null | python -c "import sys,json; print json.load(sys.stdin)['drone_connect_to']")

echo $DRONEAPIPORT

export MODIFIEDPORT=$(sed "s/droneapi/drone-proxy/g" <<< "$DRONEAPIPORT")

echo $MODIFIEDPORT

sleep 5


