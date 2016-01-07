#!/usr/bin/bash

#This script is used to do some operations on files
#such creating a new file, deleting a file and modifying a file

directory="/home/mininet/SDNCompetition/switchInfo"
#file="$directory/$1"
#operation="$2"

if [ ! -d "$directory" ]; then
	mkdir "$directory"
fi

file="$directory/$1"
operation="$2"

if [ ! -f "$file" ]; then
	touch "$file"
	echo 0 > $file
fi

#read file, increase/decrease the number and assign to variable
if [ "$operation" = "increase" ]; then
	read -r num < $file
	let "num += 1"
	echo $num > $file
fi

if [ "$operation" = "decrease" ]; then
	read -r num < $file
	let "num -= 1"
	echo $num > $file
fi

if [ "$operation" = "delete" ]; then
	rm $file
fi

if [ "$operation" = "set" ]; then
	echo $3 > $file
fi
