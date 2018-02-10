# baselineDockerfile

This dockerfile builds the baseline for the DroneRESTAPI. It installs python, the required python modules, the MAVProxy and finally the Ardupilot. It contains no RUN command as the image is intended as a baseline for other images.

To rebuild the image, execute the command:

```
docker build -t lesterthomas/sitlbase:1.0 .
```