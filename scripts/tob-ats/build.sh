#!/bin/bash
set -x
if [ $# -eq 4 ];then
    pro=$1
    cdate=$2
    betag=$3
    fetag=$4
else
    exit 400
fi

srcpath1="/opt/deploy/coderepo/tob/tob-ats/"
destpath="/opt/deploy/repo/project/tob/tob-ats/"
codepath1="/opt/deploy/repo/project/tob/tob-ats/tob-ats/"

cpath=`pwd`

if [ ! -d $srcpath1 ];then
   cd /opt/deploy/coderepo/tob/;git clone git@192.168.1.199:web/tob-ats.git
else
   cd $srcpath1;git checkout -f $fetag;git pull
fi

if [ ! -d $destpath ];then
    mkdir $destpath -p
fi

rsync -avz --exclude=".git/" --delete $srcpath1 $codepath1
if [ $? -ne 0 ];then
    exit 400
fi
cd $codepath1
mkdir bootstrap/cache -p
if [ $? -ne 0 ];then
   exit 404
fi
cd $destpath
echo "构建开始：`date +"%Y-%m-%d %H:%M:%S"`"
docker build --no-cache=true -t docker.ifchange.com/projects/$pro:latest .
echo “构建结束：`date +"%Y-%m-%d %H:%M:%S"`”
docker tag  docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
echo "推送开始：`date +"%Y-%m-%d %H:%M:%S"`"
docker push docker.ifchange.com/projects/$pro:$cdate
echo "推送结束：`date +"%Y-%m-%d %H:%M:%S"`"
