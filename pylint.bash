#!/bin/bash


echo "Capturing pylint info for all files"


for file_name in *.py 
do 
	echo "Processing $file_name"
	result_string="${file_name/.py/.lint}"
	pylint --output-format=parseable --reports=no $file_name > $result_string

done
	tail -n 2 *.lint
exit 0
