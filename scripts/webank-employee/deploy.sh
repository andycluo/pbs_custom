#!/bin/bash

if [ $# -ne 3 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
fi

docker pull $img
cid=`docker ps --filter "NAME=$pname" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi
port=19090
if [ $menv == 'demo' ];then
    port=19091
    menv='test'
fi

LOGPATH="/opt/log/$pname/"
if [ ! -d $LOGPATH ];then
    mkdir $LOGPATH -p
fi

docker run -d --cap-add=SYS_PTRACE -p $port:9090 -e APP_ENV=$menv -v /opt/log/$pname/:/opt/log/ -v /opt/wwwroot/conf/:/opt/wwwroot/conf/ --name=$pname $img /root/run.sh $menv

