 docker stop $(docker ps -a -f name=droneapi -q)
 docker rm $(docker ps -a -f name=droneapi -q)
