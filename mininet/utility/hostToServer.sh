#!/usr/bin/bash

#The parameters for this script are: host port, server mac address

directory="/home/mininet/SDNCompetition/hostToServer/"

if [ ! -d $directory ]; then
	mkdir $directory
fi

if [ $2 == "delete" ]; then
	rm $directory$1
else
	if [ ! -f $directory$1 ]; then
		touch $directory$1
	fi

	echo $2 > $directory$1
fi
