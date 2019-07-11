#!/bin/bash
set -x
if [ $# -eq 1 ];then
    betag=$1
else
    exit 400
fi

BEPATH=/opt/deploy/coderepo/tob/custom/be/
CPATH=/opt/deploy/repo/project/tob/custom/base
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
echo $CPATH
docker build --no-cache=true -t docker.ifchange.com/projects/tobcustombase:v1 . >> /opt/log/docker_build.log 
docker push docker.ifchange.com/projects/tobcustombase:v1 >> /opt/log/docker_build.log
