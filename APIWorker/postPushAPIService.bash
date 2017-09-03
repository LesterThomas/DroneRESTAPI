#!/bin/bash


docker push lesterthomas/droneapiworker:$VERSION
MINOR_VERSION=$((MINOR_VERSION+1))
echo "$MINOR_VERSION" > "MinorVersion.txt"
