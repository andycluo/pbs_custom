#!/bin/bash

if [ $# -eq 2 ];then
    menv=$2
elif [ $# -eq 3 ];then
    menv=$2
    pro=$3
else
    echo 'Just build base.'
fi
cdate=`date +"%Y%m%d%H%M%S"`
if [ $1 == 'web' ];then
    scpname="/opt/wwwroot/deploy/greentown/deploy.sh"
    img="docker.ifchange.com/projects/tobcustom/greentown:$cdate"    
    port=39001
    sh build_fe.sh greentown $cdate $pro
elif [ $1 == 'base' ];then
    sh build_base.sh master-customize 
    exit 200
else
    scpname="/opt/wwwroot/deploy/greentown/deploy_ats.sh"
    img="docker.ifchange.com/projects/tobcustom/greentown-ats:$cdate"
    port=39101
    sh build_ats.sh greentown $cdate customize-greentown customize-greentown
fi

ansible custom_$menv -m shell -a "$scpname greentown $img $menv $port"
