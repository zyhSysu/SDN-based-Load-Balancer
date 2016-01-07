#!/usr/bin/bash

#This script trys to find the server with lightest workload
#to server the user requests

#Here we assump the first switch: switch 1 is the gateway switch
#connected to our simulator. So we balance the flow among the rest
#of the switches

directory="/home/mininet/SDNCompetition/switchInfo"

#let numOfFile=`ls $direcotry -l | wc -l`-1

serverDst1="00:00:00:00:00:01"
numberOfConnections1=`cat $directory/$serverDst1`

serverDst2="00:00:00:00:00:02"
numberOfConnections2=`cat $directory/$serverDst2`

if [ $numberOfConnections1 -gt $numberOfConnections2 ]; then
	echo $serverDst2
	echo $numberOfConnections2
else
	echo $serverDst1
	echo $numberOfConnections1
fi

#for file in ${directory}/*
#do
#	tempNum=`cat $file`

#	if [ $tempNum -lt $numOfHosts ]; then
#		serverDst=$file
#		numOfHosts=$tempNum
#	fi
#done

#echo ${serverDst:14}
#echo $numOfHosts
