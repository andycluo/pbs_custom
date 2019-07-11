#!/bin/bash 

if [ $# -ne 3 ];then 
    exit 404 
else
    pname=$1
    img=$2
    menv=$3
fi
 
port=18080
args="--cpus=5 --memory=2g --memory-swap=3g"
if [ $menv == 'test3' ];then
    port=28080
    pname="tob-resume_test3-service"
    menv='test'
elif [ $menv == 'pro' ];then
    total=`free -g|awk '/Mem/{print $2}'`
    if [ $total -ge 14 ];then
        real="7g"
        swap="8g"
    else
        real="3g"
        swap="4g"
    fi
    args="--cpus=8 --memory=$real --memory-swap=$swap"
fi
logpath="/opt/log/$pname/"
if [ -z $logpath ];then
    mkdir $logpath -p
fi
sudo chown nobody. $logpath -R
cid=`docker ps --filter "NAME=$pname" --format "{{.ID}}"` 
if [ ! -z $cid ];then 
    docker stop $cid 
    docker rm $cid 
fi 
host=`/usr/sbin/ifconfig em1|sed -n 2p|awk '{print $2}'`
docker pull $img
    
docker run -d $args -p $port:8080 -v $logpath:/opt/tomcat/logs/ --name=$pname $img /root/run.sh $menv 
sleep 20 
echo '状态监测：' 
n=1
while (( $n <= 5 ))
do 
   curl http://$host:$port/tobhealthcheckstatus.jsp
   if [ $? -ne 0 ];then
      continue
   else
      break
   fi
done
