docker stop $(docker ps -a -q -f name=droneapi)
docker rm $(docker ps -a -q -f name=droneapi)
docker build -f APIDockerBuild/Dockerfile -t lesterthomas/droneapi:1.8.9 .
docker run -p 1235:1234 --link redis:redis -e "DRONEAPI_URL=http://localhost:1235" -e "DOCKER_HOST_IP=172.17.0.1" -e "DOCKER_DRONESIM_IMAGE=lesterthomas/dronesim:1.7" --name droneapi lesterthomas/droneapi:1.8.9 &