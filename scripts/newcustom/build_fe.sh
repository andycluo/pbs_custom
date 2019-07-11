#!/bin/bash
set -x
if [ $# -eq 3 ];then
    pro=$1
    cdate=$2
    fetag=$3
else
    exit 400
fi

FEPATH=/opt/deploy/coderepo/tob/custom/fe/
CPATH=/opt/deploy/repo/project/tob/custom/fe
DESTFE=$CPATH/fe/
CODEPAR=`dirname $FEPATH`

function checkDir(){
    if [ ! -d $1 ];then
        mkdir $1 -p
    else
        echo "$1 aready exists"
    fi
}

function getCode(){
    proname=$1
    code=$2
    tag=$3
    if [ ! -d $code ];then
        cd $CODEPAR;git clone git@192.168.1.199:web/${proname}.git
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
checkDir $DESTFE
checkDir $CODEPAR
getCode fe $FEPATH $fetag

for dir in assets dist
do
    if [ $dir == 'assets' ];then
        rsync -avg --delete --exclude='.git/'  $FEPATH$dir/$pro $DESTFE$dir/
    else
        rsync -avg --delete --exclude='.git/'  $FEPATH$dir/ $DESTFE$dir/
    fi
    if [ $? -ne 0 ];then
        echo 'Sync code be failed'
        exit 400
    fi
done
cd $CPATH
if [ -f 'code/fe.zip' ];then
    rm -f code/fe.zip
fi
zip -r code/fe.zip fe
docker build --build-arg CUSTOM=$pro -t docker.ifchange.com/projects/tobcustom/$pro:$cdate . >> /opt/log/docker_build.log 
docker push docker.ifchange.com/projects/tobcustom/$pro:$cdate >> /opt/log/docker_build.log
