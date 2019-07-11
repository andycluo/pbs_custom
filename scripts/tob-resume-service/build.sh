#!/bin/bash

cpath=/opt/deploy/repo/project/tob/tobresumeservice/
CODEPATH=/opt/deploy/coderepo/tob/tob-resume-service
CODE=$cpath/code

if [ $# -ne 4 ];then
   echo 'args error'
   exit 400
else
   pro=$1
   cdate=$2
   betag=$3
   fetag=$4
fi 

cd $CODEPATH
sh build.sh $betag
if [ $? -ne 0 ];then
    echo 'Update code failed'
    exit 400
fi

cd $cpath
if [ -f 'ROOT.war' ];then
    rm -f ROOT.war
fi

if [ -f "$CODEPATH/target/tobResumeService-0.0.1-SNAPSHOT.war" ];then
    cp $CODEPATH/target/tobResumeService-0.0.1-SNAPSHOT.war ROOT.war
else
    echo "$CODEPATH/target/tobResumeService-0.0.1-SNAPSHOT.war not found"
    exit 404
fi

docker build --no-cache -t docker.ifchange.com/projects/$pro:latest .
docker tag docker.ifchange.com/projects/$pro:latest docker.ifchange.com/projects/$pro:$cdate
docker push docker.ifchange.com/projects/$pro:$cdate
