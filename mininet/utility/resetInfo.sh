#!/usr/bin/bash

#This shell script is used to create switchInfo directory
#and the switch information file for each switch
#We take switch number as scriput parameter
#and we create host mac address manually
#and the switch is less than 100

index=1
fileName="00:00:00:00:00:01"
directory="/home/mininet/SDNCompetition/switchInfo"

if [ ! -d $directory ]; then
	mkdir $directory
fi

while [ $index -le $1 ]
do
	touch "$directory/$fileName"
	echo 0 > "$directory/$fileName"
	let "index++"
	
	let "temp=index-1"
	fileName=${fileName/$temp/$index}
	echo $fileName
done
