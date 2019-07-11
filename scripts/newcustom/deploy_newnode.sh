#!/bin/bash
set -x
if [ $# -ne 4 ];then
    exit 404
else
    pname=$1
    img=$2
    menv=$3
    port=$4
fi

if [ $pname == 'ka-demo' ];then
    ptname='ka'
else
    ptname=$pname
fi
if [ $menv == 'test' ];then
    menv='testing'
    mhost="--add-host ${pname}.testing2.ifchange.com:10.9.10.2 --add-host partner-${ptname}.testing2.ifchange.com:10.9.10.2"
else
    menv='production'
    mhost="--add-host ${pname}.ifchange.com:192.168.8.4 --add-host partner-${ptname}.ifchange.com:192.168.8.4"
fi
pname=$pname"-node"
LOGPATH="/opt/log/tob-node/$pname"
MODULEPATH="/opt/wwwroot/tob/ifchangefe/${pname}_modules/"
webport=$port
#fepath="/opt/wwwroot/tob/ifchangefe/${pname}/fe/"
#viewpath="/opt/wwwroot/tob/ifchangefe/${pname}/views/"
destpath="/opt/wwwroot/tob/ifchangefe/${pname}"

portmaps="-p $webport:8161"	

for newpath in $LOGPATH $destpath $MODULEPATH
do
    if [ ! -d $newpath ];then
        sudo mkdir $newpath -p
    fi
    sudo chown nobody. $newpath -R
done

docker pull $img
cid=`docker ps -a --filter "NAME=$pname" --format "{{.ID}}"`
if [ ! -z $cid ];then
    docker stop $cid
    docker rm $cid
fi
#docker run -d  $portmaps -e NODE_ENV=$menv  $mhost -v $LOGPATH:/opt/log/tob/node/ -v $fepath:/opt/wwwroot/ifchange/fe/fe/ -v $viewpath:/opt/wwwroot/ifchange/fe/views/ -v $MODULEPATH:/opt/wwwroot/ifchange/fe/node_modules/ -v /etc/localtime:/etc/localtime --name=$pname $img /root/node.sh $menv
docker run -d  $portmaps -e NODE_ENV=$menv  $mhost -v $LOGPATH:/opt/log/tob/node/ -v $MODULEPATH:/opt/wwwroot/ifchange/fe/node_modules/ -v /etc/localtime:/etc/localtime --name=$pname $img /root/node.sh $menv
lpath=`docker inspect -f '{{.GraphDriver.Data.MergedDir}}' $pname`
for dname in fe views
do
    if [ ! -d "$destpath/$dname" ];then
        sudo cp -r $lpath/opt/wwwroot/ifchange/fe/$dname $destpath/
    else
        sudo rsync -rlptD  $lpath/opt/wwwroot/ifchange/fe/$dname/ $destpath/$dname/
    fi
done
#sudo rsync -rlptD  $lpath/opt/wwwroot/ifchange/fe/fe/ $fepath
#sudo rsync -rlptD  $lpath/opt/wwwroot/ifchange/fe/views/ $viewpath
