#!/bin/bash
set -x
if [ $# -eq 2 ];then
    pro=$1
    cdate=$2
else
    exit 400
fi

destpath="/opt/deploy/repo/project/tob/custom/docker-employee/"

cd $destpath
echo "构建开始：`date +"%Y-%m-%d %H:%M:%S"`"
docker build  --no-cache=true -t hub.ifchange.com/tobcustom/$pro-employee:latest .
echo “构建结束：`date +"%Y-%m-%d %H:%M:%S"`”
docker tag  hub.ifchange.com/tobcustom/$pro-employee:latest hub.ifchange.com/tobcustom/$pro-employee:$cdate
echo "推送开始：`date +"%Y-%m-%d %H:%M:%S"`"
docker push hub.ifchange.com/tobcustom/$pro-employee:$cdate
echo "推送结束：`date +"%Y-%m-%d %H:%M:%S"`"
