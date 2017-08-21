# DroneRESTAPI

This project provides a simple hypermedia REST API on top of the Python SDK (http://python.dronekit.io/).

## Installation

### Simple installation

This is available as a two Docker images containing the API and a Drone simulator (ArduCopter flight-controller running in a simulator-SITL). On a Docker environment, simply run the following command (which will install the image if not already installed).

```
docker run -p 1235:1234 lesterthomas/droneapi:1.7
```

The docker image will expose the API on port `1235`. Test the API in a browser or POSTMAN by going to the root of the API `http://localhost:1235/`.

There is a static HTML5 web page built on top of the API that gives a simple demonstration set of controls. This is available at `http://localhost:1235/static/app/index.html`.


### Detailed installation

To install the API and simulator outside of Docker, you can follow the commands in the three Dockerfiles (the instructions are based on  http://python.dronekit.io/guide/quick_start.html#installation). 

The first Dockerfile (baselineDockerfile/Dockerfile) is for the baseline installation of python development environment, MAVProxy, dronekit and Ardupilot. 

The second Dockerfile (APIDockerBuild/Dockerfile) installs the API (which is a single Python script in rest.py) and the static HTML5 client.

The third Dockerfile (DroneSIMDockerBuild) installs a drone simulator


## Using API

Using a browser or REST API Client (I recommend Postman), browse to the root of the server. `http://localhost:1234`

The returned payload is the EntryPoint (or homepage) of the API and shows the APIs available. The following images capture a sample of browsing through the API.

![EntryPoint](Images/EntryPoint.png)
![Vehicle Collection](Images/VehicleCollection.png)
![Vehicle Details](Images/Vehicle1.png)
![Vehicle Actions](Images/Vehicle1Actions.png)



## Building Docker image

The Dockerfile builds on top of the baselineDocker file (that creates the `lesterthomas/sitlbase:1.0` image). To re-build the Docker image execute the command:

```docker build -t lesterthomas/dronesim:1.5 .```

## Python module documentation

The python ```pdoc``` documentation is at:

[droneAPIMain](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIMain.m.html): The main module that sets-up the API server.

[droneAPIUtils](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIUtils.m.html): Utility functions that manage global data structures and Redis database.

Modules for each end-point:


- /vehicle : [droneAPIVehicleIndex](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIVehicleIndex.m.html) 
	- /vehicle/(.*) : [droneAPIVehicleStatus](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIVehicleStatus.m.html) 
		- /vehicle/(.*)/action : [droneAPIAction](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIAction.m.html)  
		- /vehicle/(.*)/homeLocation : [droneAPIHomeLocation](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIHomeLocation.m.html)  
		- /vehicle/(.*)/mission : [droneAPIMission](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIMission.m.html) 
		- /vehicle/(.*)/authorizedZone : [droneAPIAuthorizedZone](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIAuthorizedZone.m.html) 
		- /vehicle/(.*)/simulator : [droneAPISimulator](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPISimulator.m.html) 
- /admin : [droneAPIAdmin](http://htmlpreview.github.io/?https://github.com/LesterThomas/DroneRESTAPI/blob/master/droneAPIAdmin.m.html) 




