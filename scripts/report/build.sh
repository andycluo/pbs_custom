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

srcpath1="/opt/deploy/coderepo/tob/report/"
destpath="/opt/deploy/repo/project/tob/report/"
codepath1="/opt/deploy/repo/project/tob/report/report/"
codedir=`dirname $codepath1`

cpath=`pwd`

if [ ! -d $srcpath1 ];then
   cd /opt/deploy/coderepo/tob/;git clone git@192.168.1.199:web/report.git
else
   cd $srcpath1;git checkout -f $fetag;git pull
fi
for md in $destpath $codedir
do
    if [ ! -d $md ];then
        mkdir $md -p
    fi
done
rsync -avz --exclude=".git/" --delete $srcpath1 $codepath1
if [ $? -ne 0 ];then
    exit 400
fi
cd $codepath1
mv bootstrap/{autoload.php.docker,autoload.php}
if [ $? -ne 0 ];then
   exit 404
fi
mkdir bootstrap/cache -p
if [ $? -ne 0 ];then
   exit 404
fi
cd $destpath
docker build -t docker.ifchange.com/projects/$pro:latest .
docker tag  docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate
