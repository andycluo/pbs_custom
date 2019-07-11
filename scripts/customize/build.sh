#!/bin/bash
set -x
if [ $# -eq 3 ];then
    pro=$1
    cdate=$2
    betag=$3
else
    exit 400
fi

srcpath1="/opt/deploy/coderepo/tob/customize/"
destpath="/opt/deploy/repo/project/tob/customize/"
codepath1="/opt/deploy/repo/project/tob/customize/customize/"

cpath=`pwd`

if [ ! -d $srcpath1 ];then
   cd /opt/deploy/coderepo/tob/;git clone git@192.168.1.199:backend/customize.git
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
cd $destpath
docker build  -t docker.ifchange.com/projects/$pro:latest .
docker tag  docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate
