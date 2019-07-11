#!/bin/bash

if [ $# -ne 3 ];then
    exit
else
    menv=$1
    tag=$2
    ftag=$3
fi

cadte=`date +"%Y%m%d%H%M%S"`
sh build.sh demo $cadte $tag $ftag
if [ $? -ne 0 ];then
    echo 'build failed'
    exit
fi
img="docker.ifchange.com/projects/demo:$cadte"
scrp="/opt/wwwroot/deploy/demo/deploy.sh"
ansible demo_$menv -m shell -a "$scrp demo $img $menv"
if [ $? -ne 0 ];then
    echo 'deply failed'
    exit
fi

