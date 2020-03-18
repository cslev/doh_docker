#!/bin/bash

sudo echo "Removing running docker images"

for i in $(sudo docker ps -a|grep doh_docker| awk '{print $1}')
do
  sudo docker rm $i
done


sudo echo "Removing the docker images themselves"

for i in $(sudo docker images|grep doh_docker| awk '{print $3}')
do
  sudo docker rmi $i
done



