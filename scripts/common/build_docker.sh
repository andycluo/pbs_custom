#!/bin/bash
set -x
if [ $# -eq 3 ];then
    pro=$1
    betag=$2
    cdate=$3
else
    exit 400
fi

BEPATH=/opt/deploy/coderepo/new/newbe/be/
CPATH=/opt/deploy/repo/project/tob/custom/newbase
DESTBE=$CPATH/code/be/
CODEPAR=`dirname $BEPATH`

function checkDir(){
    if [ ! -d $1 ];then
        mkdir $1 -p
    else
        echo "$1 aready exists"
    fi
}

function getCode(){
    code=$1
    tag=$2
    if [ ! -d $code ];then
        cd $CODEPAR;git clone git@192.168.1.199:web/be.git
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
checkDir $DESTBE
checkDir $CPATH
checkDir $CODEPAR
getCode $BEPATH $betag

rsync -avg --exclude='.git/'  $BEPATH $DESTBE
if [ $? -ne 0 ];then
    echo 'Sync code be failed'
    exit 400
fi
cd $CPATH
docker build --no-cache=true -t docker.ifchange.com/projects/$pro:latest . >> /opt/log/docker_build.log 
docker tag docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate >> /opt/log/docker_build.log
