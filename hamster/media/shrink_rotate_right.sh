#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: $0 <file_to_rotate>"
	exit
fi

mkdir -p original
mv "$1" original

time avconv -i "original/$1" -vf transpose=1 -s 504x900 -c:a copy "$1"
