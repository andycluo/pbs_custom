#!/bin/bash
###
#dist全量
#sh  newdeploy.sh fe test haier master-haier
#web部署
#sh newdeploy.sh base test haier master-haier ''
###

if [ $# -eq 4 ];then
    func=$1
    menv=$2
    pro=$3
    tag=$4
else
    echo 'Just build error.'
    exit
fi
cdate=`date +"%Y%m%d%H%M%S"`

hostg="custom_${menv}"
destpath="/opt/wwwroot/deploy/haier/"
zfile="/opt/wwwroot/deploy/haier/${pro}.zip"
fedeppath="/opt/wwwroot/tob/web/haier/fe/"
ansible $hostg -m file -a "path=$destpath state=directory recurse=yes owner=pubuser group=pubuser"
if [ $func == 'fe' ];then
    sname="/opt/deploy/pbs/scripts/haier/deploycode.sh"
    scpname="/opt/wwwroot/deploy/haier/deploycode.sh"
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    sh build_fe.sh $pro $cdate $tag $menv
    ansible $hostg -m shell -a "$scpname $zfile $fedeppath"
elif [ $func == 'base' ];then
    sname="/opt/deploy/pbs/scripts/haier/deploy_be.sh"
    scpname="/opt/wwwroot/deploy/haier/deploy_be.sh"
    img="docker.ifchange.com/projects/haier:$cdate"    
    port=39003
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    sh build_be.sh haier $tag $cdate
    ansible $hostg -m shell -a "$scpname haier $img $menv $port"
fi
