 #!/bin/bash

 sleep 15
 sleep $1
 zoneString='{"zone":{"shape":{"name":"circle","radius":500}}}'
 curl --data $zoneString -X POST http://localhost:1235/vehicle/$1/authorizedZone
 echo $zoneString

 sleep 50



