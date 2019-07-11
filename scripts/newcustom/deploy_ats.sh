#!/bin/bash

if [ $# -ne 4 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
    port=$4
fi

dname="${pname}-ats"
args="--cap-add=SYS_PTRACE --memory=1g --memory-swap=1.5g"
cip=`/usr/sbin/ifconfig em1|awk '/inet /{print $2}'`
conf="/opt/wwwroot/conf/"
if [ $menv = 'pro' ];then
    args="--cap-add=SYS_PTRACE --memory=3g --memory-swap=3g"
fi
docker pull $img
cid=`docker ps -a --filter "NAME=$dname" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi
if [ $cip == '192.168.8.219' ];then
    marg="$menv 219"
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

sfs=""
if [ $pname == 'iflytek' ];then
    sharepath='/opt/wwwroot/share_files/iflytek'
    if [ ! -d $sharepath ];then
        mkdir $sharepath -p
    fi
    sfs="-v /opt/wwwroot/share_files/iflytek:/opt/wwwroot/share_files/iflytek"
fi

docker run -d $args -p $port:9090 -e APP_ENV=$menv $sfs -v $LOGPATH:/opt/log/ -v $conf:/opt/wwwroot/conf/ --name=$dname $img /root/run.sh $marg
