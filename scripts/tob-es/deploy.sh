#!/bin/bash 

if [ $# -ne 3 ];then 
    exit 404 
else
    pname=$1
    img=$2
    menv=$3
fi 
 
port=18081
if [ $menv = 'test3' ];then
    menv='test'
    port=28081
    pname="${pname}_test3"
fi
logpath="/opt/log/$pname/"
if [ -z $logpath ];then
   mkdir $logpath -p
fi
sudo chown nobody. $logpath -R
cid=`docker ps -a --filter "NAME=$pname" --format "{{.ID}}"` 
if [ ! -z $cid ];then 
    docker stop $cid 
    docker rm $cid 
fi 

docker pull $img
docker run -d  --memory=2g --memory-swap=3g -p $port:8080 -v $logpath:/opt/tomcat/logs/ --name=$pname $img /root/run.sh $menv 
