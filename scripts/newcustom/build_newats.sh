#!/bin/bash
set -x
if [ $# -eq 2 ];then
    pro=$1
    cdate=$2
else
    exit 400
fi

destpath="/opt/deploy/repo/project/tob/custom/docker-ats/"

cd $destpath
echo "构建开始：`date +"%Y-%m-%d %H:%M:%S"`"
docker build  --no-cache=true -t docker.ifchange.com/projects/$pro:latest .
echo “构建结束：`date +"%Y-%m-%d %H:%M:%S"`”
docker tag  docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
echo "推送开始：`date +"%Y-%m-%d %H:%M:%S"`"
docker push docker.ifchange.com/projects/$pro:$cdate
echo "推送结束：`date +"%Y-%m-%d %H:%M:%S"`"
