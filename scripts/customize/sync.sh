#!/bin/bash

if [ $# -ne 2 ];then
    exit
else
    tag=$1
    menv=$2
fi

cadte=`date +"%Y%m%d%H%M%S"`
sh build.sh 'custom_admin' $cadte $tag
if [ $? -ne 0 ];then
    echo 'build failed'
    exit
fi
img="docker.ifchange.com/projects/custom_admin:$cadte"
scrp="/opt/wwwroot/deploy/custom_admin/deploy.sh"
ansible cusadmin_$menv -m shell -a "$scrp 'custom_admin' $img $menv"
if [ $? -ne 0 ];then
    echo 'deply failed'
    exit
fi
