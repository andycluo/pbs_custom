#!/bin/bash
set -x
if [ $# -ne 4 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
    port=$4
fi

webargs="--memory=1g --memory-swap=1.5g"
gmconf='/opt/wwwroot/conf/'
pro="$pname-web"
LOGPATH="/opt/log/$pro/"

if [ $menv == 'test' ];then
    menv='testing2'
else
    menv='production'
    webargs="--memory=3g --memory-swap=4g"
fi

for log in $LOGPATH
do
    if [ ! -d $log ];then
        mkdir $log -p
    fi
    sudo chown nobody. $log -R
done

docker pull $img
cid=`docker ps -a --filter "NAME=$pro" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi
docker run -d  $webargs -p $port:80  -e APP_ENV=$menv -e SUBNAME=$pname -v $LOGPATH:/opt/log/ -v /opt/data/tobExportResume/:/opt/export_resume/  -v $gmconf:/opt/wwwroot/conf/ --name=$pro $img /root/run.sh $menv $pname
