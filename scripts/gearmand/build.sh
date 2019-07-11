#!/bin/bash

pro=$1
cdate=$2
cpath=/opt/deploy/repo/$pro/

if [ $# -ne 1 ];then
   menv=test
else
   menv=$1
fi 
cd $cpath

docker build --no-cache -t docker.ifchange.com/app/$pro:latest .
docker tag docker.ifchange.com/app/$pro:latest docker.ifchange.com/app/$pro:$cdate
docker push docker.ifchange.com/app/$pro:$cdate
