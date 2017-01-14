# DroneRESTAPI

This project provides a simple hypermedia REST API on top of the Python SDK (http://python.dronekit.io/).

##Installation

To install dronekit on Linux (full instructions at http://python.dronekit.io/guide/quick_start.html#installation)

If not already installed, install pip and python-dev:

'''
sudo apt-get install python-pip python-dev
'''

pip is then used to install dronekit:

'''
sudo pip install dronekit
'''


The REST API is a single script in rest.py. Download or clone this from GitHub and then type:

'''
python rest.py 1234
'''

Where '1234' is the port where you want the REST API to be exposed.


##Using API

Using a browser or REST API Client (I recommend Advanced REST Client which is a Chrome Extension), browse to the root of the server. 'http://localhost:1234'

The returned payload is the EntryPoint (or homepage) of the API and shows the APIs available. The following images capture a sample of browsing through the API.

![Images/EntryPoint.png]
![Images/VehicleCollection.png]
![Images/Vehicle1.png]
![Images/Vehicle1Actions.png]






