#!/bin/bash


docker push lesterthomas/droneapiworker:$VERSION
MINOR_VERSION=$((MINOR_VERSION))
echo "$MINOR_VERSION" > "MinorVersion.txt"
