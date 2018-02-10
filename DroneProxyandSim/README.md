# droneProxyandSim

The API Server dynamically installs either DroneProxy (Mavlink proxy) or DroneSIM (Full SITL simulated drones). To connect to a real drone, it creates the DroneProxy which proxies the Mavlink commands; To simulate and test a simulated drone it creates a DroneSIM which is a SITL simulation running the ArduCopter code.

Both of these images are built on a common baseline image. Once running, the API Server can not distinguish between a simulated drone or a proxy to a real drone.

