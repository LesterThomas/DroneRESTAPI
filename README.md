# DroneRESTAPI

This project provides a simple hypermedia REST API on top of the Python SDK (http://python.dronekit.io/).

##Installation

###Simple installation

This is available as a single Docker image containing the API and a ArduCopter flight-controller running in a simulator (SITL). On a Docker environment, simply run the following command (which will install the image if not already installed).

```
docker run -p 1235:1234 lesterthomas/dronesim:1.5
```

The docker image will expose the API on port `1235`. Test the API in a browser or POSTMAN by going to the root of the API `http://localhost:1235/`.

There is a static HTML5 web page built on top of the API that gives a simple demonstration set of controls. This is available at `http://localhost:1235/static/app/index.html`.


###Detailed installation

To install the API and simulator outside of Docker, you can follow the commands in the two Dockerfiles (the instructions are based on  http://python.dronekit.io/guide/quick_start.html#installation). 

The first Dockerfile is for the baseline installation of python development environment, MAVProxy, dronekit and Ardupilot. 

The second Dockerfile installs the API (which is a single Python script in rest.py) and the static HTML5 client.


##Using API

Using a browser or REST API Client (I recommend Postman), browse to the root of the server. `http://localhost:1234`

The returned payload is the EntryPoint (or homepage) of the API and shows the APIs available. The following images capture a sample of browsing through the API.

![EntryPoint](Images/EntryPoint.png)
![Vehicle Collection](Images/VehicleCollection.png)
![Vehicle Details](Images/Vehicle1.png)
![Vehicle Actions](Images/Vehicle1Actions.png)



##Building Docker image

The Dockerfile builds on top of the baselineDocker file (that creates the `lesterthomas/sitlbase:1.0` image). To re-build the Docker image execute the command:

```docker build -t lesterthomas/dronesim:1.5 .```


