#!/bin/bash

if [ $# -ne 3 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
fi

port=19002
dname=${pname}
args="--cap-add SYS_PTRACE --cpus=1 --memory=1g --memory-swap=1.5g"
cip=`/usr/sbin/ifconfig em1|awk '/inet /{print $2}'`
conf="/opt/wwwroot/conf/"
if [ $menv = 'test3' ];then
    menv='test3'
    port=29002
    dname="tob-test3-ats"
    conf="/opt/wwwroot/conf_test3/"
elif [ $menv = 'pro' ];then
    args="--cap-add=SYS_PTRACE --memory=3g --memory-swap=3g"
fi
docker pull $img
cid=`docker ps -a --filter "NAME=$dname" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi
if [ $cip == '192.168.8.30' ];then
    marg="$menv 30"
elif [ $cip == '10.9.10.16' ];then
    marg="$menv 16"
else
    marg="$menv"
fi

LOGPATH="/opt/log/$dname/"
if [ ! -d $LOGPATH ];then
    mkdir $LOGPATH -p
fi
sudo chown nobody. $LOGPATH -R

docker run -d $args -p $port:9090 -e APP_ENV=$menv -v $LOGPATH:/opt/log/ -v $conf:/opt/wwwroot/conf/ --name=$dname $img /root/run.sh $marg

