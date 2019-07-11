#!/bin/bash 

if [ $# -ne 3 ];then 
    exit 404 
else
    pname=$1
    img=$2
    menv=$3
fi 
 
cid=`docker ps --filter "NAME=$pname" --format "{{.ID}}"` 
if [ ! -z $cid ];then 
    docker stop $cid 
    docker rm $cid 
fi 
host=`/usr/sbin/ifconfig em1|sed -n 2p|awk '{print $2}'`
docker pull $img
if [ $menv == 'test' ];then
    docker run  --privileged -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e xpack.security.enabled=false -v /opt/data/elasticsearch:/opt/data/elasticsearch -v /opt/log/elasticsearch:/opt/log/elasticsearch  --name=$pname $img
else
    docker run --privileged -d -p 9200:9200 -p 9300:9300 -e xpack.security.enabled=false -v /opt/data/elasticsearch:/opt/data/elasticsearch -v /opt/log/elasticsearch:/opt/log/elasticsearch --name=$pname $img
fi
sleep 20 
echo '状态监测：' 
n=1
while (( $n <= 5 ))
do 
   curl http://$host:9200/
   if [ $? -ne 0 ];then
      continue
   else
      break
   fi
done
