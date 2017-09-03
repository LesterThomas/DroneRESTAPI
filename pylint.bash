#!/bin/bash

cd APIServer
source "pylint.bash"

cd ../APIWorker
source "pylint.bash"

exit 0

