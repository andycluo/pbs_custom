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

srcpath1="/opt/deploy/coderepo/tob/interviewer-admin/"
srcpath2="/opt/deploy/coderepo/tob/webank-employee/"
destpath="/opt/deploy/repo/project/tob/webank-employee/"
codepath1="/opt/deploy/repo/project/tob/webank-employee/interviewer-admin/"
codepath2="/opt/deploy/repo/project/tob/webank-employee/webank-employee/"

cpath=`pwd`

if [ ! -d $srcpath1 ];then
   cd /opt/deploy/coderepo/tob/;git clone git@192.168.1.199:web/interviewer-admin.git
else
   cd $srcpath1;git checkout -f $fetag;git pull
fi

if [ ! -d $srcpath2 ];then
   cd /opt/deploy/coderepo/tob/;git clone git@192.168.1.199:web/webank-employee.git
else
   cd $srcpath2;git checkout -f $betag;git pull
fi

if [ ! -d $destpath ];then
    mkdir $destpath -p
fi

rsync -avz --exclude=".git/" --delete $srcpath1 $codepath1
if [ $? -ne 0 ];then
    exit 400
fi
rsync -avz --exclude=".git/" --delete $srcpath2 $codepath2
if [ $? -ne 0 ];then
    exit 400
fi
cd $codepath2
mv bootstrap/{autoload.php.docker,autoload.php}
if [ $? -ne 0 ];then
   exit 404
fi
cd $destpath
docker build --no-cache=true -t docker.ifchange.com/projects/$pro:latest .
docker tag  docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate
