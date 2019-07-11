#!/bin/bash

if [ $# -ne 4 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
    port=$4
fi

dname="${pname}-employee"
args="--cap-add=SYS_PTRACE --memory=1g --memory-swap=1g"
conf="/opt/wwwroot/conf/"
if [ $menv = 'pro' ];then
    args="--cap-add=SYS_PTRACE --memory=3g --memory-swap=3g"
fi
if [ $menv == 'prod' ];then
    menv=pro
fi
docker pull $img
cid=`docker ps -a --filter "NAME=$dname" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi

LOGPATH="/opt/log/$dname/"
if [ ! -d $LOGPATH ];then
    mkdir $LOGPATH -p
fi
CODEPATH="/opt/wwwroot/tob/web/custom-employee/$pname"

sudo chown nobody. $LOGPATH -R
sudo chown pubuser. $CODEPATH -R
docker run -d $args -p $port:9090 -e APP_ENV=$menv -v $CODEPATH/:/opt/wwwroot/common-employee/ -v $LOGPATH:/opt/log/ -v $conf:/opt/wwwroot/conf/ --name=$dname $img /root/run.sh $marg
