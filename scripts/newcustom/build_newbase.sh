#!/bin/bash
if [ $# -eq 2 ];then
    pro=$1
    cdate=$2
else
    exit 400
fi

CPATH=/opt/deploy/repo/project/tob/custom/docker-base

cd $CPATH
docker build --no-cache=true -t docker.ifchange.com/projects/$pro:latest . >> /opt/log/docker_build.log 
docker tag docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate >> /opt/log/docker_build.log
