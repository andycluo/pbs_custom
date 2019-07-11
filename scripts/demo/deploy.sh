#!/bin/bash
set -x
if [ $# -ne 3 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
fi

LOGPATH="/opt/log/demo/"
webport=39004
webargs="--memory=1g --memory-swap=1.5g"
gmconf='/opt/wwwroot/conf/'
pros="demo"

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
for pro in $pros
do
    cid=`docker ps -a --filter "NAME=$pro" --format "{{.ID}}"`
    if [ ! -z $cid ];then
        docker stop $cid
        docker rm $cid
    fi
    docker run -d --cpus="0.1" $webargs -p $webport:80  -e APP_ENV=$menv -v $LOGPATH:/opt/log/ -v /opt/data/tobExportResume/:/opt/export_resume/ -v /opt/wwwroot/share_files/webank/:/opt/wwwroot/share_files/webank/ -v $gmconf:/opt/wwwroot/conf/ --name=$pro $img /root/run.sh $menv
done
