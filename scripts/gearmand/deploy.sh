#!/bin/bash 

if [ $# -ne 3 ];then 
    exit 404 
else
    pname=$1
    img=$2
    menv=$3
fi 
port=14730
if [ $menv == 'test3' ];then
    port=24730
    pname="gearmand_test3"
elif [ $menv == 'pro' ];then
    port=4730
fi
logpath="/opt/log/$pname/"
if [ ! -d $logpath ];then
    mkdir $logpath -p
fi
sudo chown nobody. $logpath -R
cid=`docker ps -a --filter "NAME=$pname" --format "{{.ID}}"` 
if [ ! -z $cid ];then 
    docker stop $cid 
    docker rm $cid 
fi 
docker pull $img
docker run -d --cpus="3" --memory=3.5g --memory-swap=4g -p $port:4730 -v $logpath:/opt/log/ --name=$pname docker.ifchange.com/app/gearman /root/gearman.sh
