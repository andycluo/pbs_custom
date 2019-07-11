#!/bin/bash

pro=$1
cdate=$2
cpath=/opt/deploy/repo/project/tob/$pro/

if [ $# -ne 1 ];then
   menv=test
else
   menv=$1
fi 
cd $cpath

docker build --no-cache -t docker.ifchange.com/projects/$pro:latest .
docker tag docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate
