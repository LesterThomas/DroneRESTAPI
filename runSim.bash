 #!/bin/bash
 gnome-terminal --tab -e "bash ./startDrone.bash 1" --tab -e "bash ./startDrone.bash 2" --tab -e "bash ./startDrone.bash 3" --tab -e "./startAPIServer.bash" --tab -e "./startWebServer.bash" 
