#!/bin/bash


docker push lesterthomas/droneapiserver:$VERSION

MINOR_VERSION=$((MINOR_VERSION+1))
echo "$MINOR_VERSION" > "MinorVersion.txt"
