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
args="--cap-add=SYS_PTRACE --memory=1g --memory-swap=1g"
cip=`/usr/sbin/ifconfig em1|awk '/inet /{print $2}'`
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
if [ $cip == '192.168.8.220' ];then
    marg="$menv $pname 220"
elif [ $cip == '10.9.10.12' ];then
    marg="$menv $pname 12"
else
    marg="$menv $pname"
fi

LOGPATH="/opt/log/$dname/"
if [ ! -d $LOGPATH ];then
    mkdir $LOGPATH -p
fi
CODEPATH="/opt/wwwroot/tob/web/$pname"

sfs=""
sharepath=""
if [ $pname == 'iflytek' -o $pname == 'jinke' ];then
    sharepath="/opt/wwwroot/share_files/$pname"
elif [ $pname == 'visionox' ];then
    sharepath="/opt/wwwroot/share_files/customize"
fi
if [ ! -d $sharepath ];then
    mkdir $sharepath -p
    sudo chown nobody. $sharepath  -R
fi  
if [ -z $sharepath ];then
    sfs=""
else
    sfs="-v $sharepath:$sharepath"
fi
sudo chown nobody. $LOGPATH -R
sudo chown pubuser. $CODEPATH -R
docker run -d $args -p $port:9090 -e APP_ENV=$menv $sfs -v $CODEPATH/:/opt/wwwroot/tob-ats/ -v $LOGPATH:/opt/log/ -v $conf:/opt/wwwroot/conf/ --name=$dname $img /root/run.sh $marg
