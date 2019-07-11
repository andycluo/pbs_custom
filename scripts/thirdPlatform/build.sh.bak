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

BEPATH=/opt/deploy/coderepo/tob/be/
#CPATH=/opt/deploy/repo/project/tob/tob-be
CPATH=/opt/deploy/repo/project/tob/be-web_new
CPATH2=/opt/deploy/repo/project/tob/be-work_new
DESTBE=$CPATH/code/be/
DESTBE2=$CPATH2/code/be/
CODEPAR=`dirname $BEPATH`

function checkDir(){
    if [ ! -d $1 ];then
        mkdir $1 -p
    else
        echo "$1 aready exists"
    fi
}

function getCode(){
    pro=$1
    code=$2
    tag=$3
    if [ ! -d $code ];then
        cd $CODEPAR;git clone git@192.168.1.199:web/${pro}.git
    else
        cd $code;git checkout -f $tag;git pull
    fi
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
getCode be $BEPATH $betag
checkDir $DESTBE
checkDir $DESTBE2

rsync -avg --delete --exclude='.git/'  $BEPATH $DESTBE
rsync -avg --delete --exclude='.git/'  $BEPATH $DESTBE2
if [ $? -ne 0 ];then
    echo 'Sync code be failed'
    exit 400
fi
cd $CPATH
docker build --no-cache=true -t docker.ifchange.com/projects/tob-web:$cdate . >> /opt/log/docker_build.log 
cd $CPATH2
docker build --no-cache=true -t docker.ifchange.com/projects/tob-work:$cdate . >> /opt/log/docker_build.log 
for pro in tob-web tob-work
do
    #docker tag docker.ifchange.com/projects/$pro:$cdate docker.ifchange.com/projects/$pro:$cdate 
    docker push docker.ifchange.com/projects/$pro:$cdate >> /opt/log/docker_build.log
done
