#!/bin/bash

if [ $# -eq 4 ];then
    pro=$1
    cdate=$2
    tag=$3
    #cfgtag=$4
else
    exit 400
fi
cpath=/opt/deploy/repo/project/tob/$pro/
CODEPATH=/opt/deploy/coderepo/tob/$pro
CFG=/opt/deploy/coderepo/tob/service-config
CODEPAR=`dirname $CODEPATH`
CODE=$cpath/code

if [ ! -d $CODEPATH ];then
    cd $CODEPAR;git clone git@192.168.1.199:soa/tob-es
else
    cd $CODEPATH;git checkout -f $tag;git pull
fi
#if [ ! -d $CFG ];then
#    git clone git@192.168.1.199:soa/service-config
#else
#    cd $CFG;git checkout -f $cfgtag;git pull
#fi
#cp -a  $CFG/tobEs/application*.properties $CODEPATH/src/main/resources/

cd $CODEPATH
mvn clean
if [ $? -ne 0 ];then
    exit 400
fi
mvn package -Dmaven.test.skip=true
if [ $? -ne 0 ];then
    echo 'Build failed'
    exit 401
fi

cd $cpath
if [ -f 'ROOT.war' ];then
    rm -f ROOT.war
fi

if [ -f "$CODEPATH/target/tob-es-1.0.war" ];then
    cp $CODEPATH/target/tob-es-1.0.war ROOT.war
else
    echo "$CODEPATH/target/tob-es-1.0.war not found"
    exit 404
fi

docker build  -t docker.ifchange.com/projects/$pro:latest .
docker tag docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate
