#!/bin/bash

if [ $# -ne 3 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
fi

docker pull $img
cid=`docker ps -a --filter "NAME=$pname" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi

LOGPATH="/opt/log/$pname/"
if [ ! -d $LOGPATH ];then
    mkdir $LOGPATH -p
fi

docker run -d --cap-add=SYS_PTRACE -p 19001:9090 -e APP_ENV=$menv -v /opt/log/$pname/:/opt/log/ -v /opt/wwwroot/conf/:/opt/wwwroot/conf/ --name=$pname $img /root/run.sh $menv

