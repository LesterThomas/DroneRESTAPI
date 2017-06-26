#!/bin/bash

#expects MAJOR_VERSION and MINOR_VERSION environment variables
MINOR_VERSION=$(<"MinorVersion.txt" ) 
echo "MINOR_VERSION"
echo $MINOR_VERSION



MINOR_VERSION=$((MINOR_VERSION+1))
echo "$MINOR_VERSION" > "MinorVersion.txt"
