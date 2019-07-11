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
FEPATH=/opt/deploy/coderepo/tob/fe/
CPATH=/opt/deploy/repo/project/tob/demo
DESTBE=$CPATH/code/be/
DESTFE=$CPATH/code/fe/
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
getCode fe $FEPATH $fetag
checkDir $DESTBE
checkDir $DESTFE

rsync -avg --exclude='.git/'  $BEPATH $DESTBE
if [ $? -ne 0 ];then
    echo 'Sync code be failed'
    exit 400
fi
for dir in assets dist
do
    rsync -avg --delete --exclude='.git/'  $FEPATH$dir/ $DESTFE$dir/
    if [ $? -ne 0 ];then
        echo 'Sync code be failed'
        exit 400
    fi
done
cd $CPATH
docker build --no-cache=true -t docker.ifchange.com/projects/demo:$cdate . >> /opt/log/docker_build.log 
docker push docker.ifchange.com/projects/demo:$cdate >> /opt/log/docker_build.log
