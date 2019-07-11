#!/bin/bash 

if [ $# -ne 3 ];then 
    exit 404 
else
    pname=$1
    img=$2
    menv=$3
fi 
 
cid=`docker ps --filter "NAME=$pname" --format "{{.ID}}"` 
if [ ! -z $cid ];then 
    docker stop $cid 
    docker rm $cid 
fi 
host=`/usr/sbin/ifconfig em1|sed -n 2p|awk '{print $2}'`
docker pull $img
if [ $menv == 'test' ];then
    docker run -d -p 5671:5671 -p 5672:5672 -p 4369:4369 -p 25672:25672 -p 15671:15671 -p 15672:15672 -e LC_ALL=en_US.UTF-8 -e LANG=en_US.UTF-8 -e RABBITMQ_NODENAME=rabbitmq -v /opt/data/rabbitmq:/opt/data/rabbitmq -v /opt/log/rabbitmq:/opt/log/rabbitmq --name=$pname --hostname=rabbitmq  docker.ifchange.com/projects/rabbitmq:v1
else
    docker run -d -p 5671:5671 -p 5672:5672 -p 4369:4369 -p 25672:25672 -p 15671:15671 -p 15672:15672 -e LC_ALL=en_US.UTF-8 -e LANG=en_US.UTF-8 -v /opt/data/rabbitmq:/opt/data/rabbitmq -v /opt/log/rabbitmq:/opt/log/rabbitmq  --name=$pname  docker.ifchange.com/projects/rabbitmq:v1
fi
