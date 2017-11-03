echo 'Loading API Servers'
ab -n 10000 -c 5 -H "APIKEY:8f4ede68-9192-4f" http://test.droneapi.net/vehicle?status=true
sleep 2
echo 'Loading 2 worker'
ab -n 100 -c 5 -H "APIKEY:e3f13003-cebc-4e" http://test.droneapi.net/vehicle/9710d87a/homeLocation
sleep 2
