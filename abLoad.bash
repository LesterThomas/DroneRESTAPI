echo 'Loading API Servers'

ab -n 1000 -c 10 -H "APIKEY:8f4ede68-9192-4f" http://droneapi.ddns.net/vehicle?status=true

echo 'Loading 2 worker'
ab -n 100 -c 10 -H "APIKEY:8f4ede68-9192-4f" http://droneapi.ddns.net/vehicle/b4617ff2/homeLocation
