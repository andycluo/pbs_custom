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

BEPATH=/opt/deploy/coderepo/tob/custom/newnode/ifchangefe
CPATH=/opt/deploy/repo/project/tob/custom/docker-node
#CPATH=/opt/deploy/repo/project/tob/custom/newnode
DESTBE=$CPATH/code/$pro
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
        cd $CODEPAR;git clone git@192.168.1.199:ifchange/fe.git $code
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
getCode  $BEPATH $betag
checkDir $DESTBE

rsync -avg --delete --exclude='.git/'  $BEPATH/ $DESTBE/
if [ $? -ne 0 ];then
    echo 'Sync code be failed'
    exit 400
fi
cd $CPATH
dirs=`ls code/ |grep -v $pro`
echo > .dockerignore
for d in $dirs
do
    echo code/$d >> .dockerignore
done
docker build --no-cache=true --build-arg proname=$pro -t hub.ifchange.com/tobcustom/$pro"-node":$cdate . >> /opt/log/docker_build.log 
docker push hub.ifchange.com/tobcustom/$pro"-node":$cdate >> /opt/log/docker_build.log
