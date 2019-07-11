#!/bin/bash
###
#dist全量
#sh  newdeploy.sh fe test talentrecommend master-haier
#web部署
#sh newdeploy.sh base test talentrecommend master-haier
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
destpath="/opt/wwwroot/deploy/democustom/"
zfile="/opt/wwwroot/deploy/democustom/${pro}.zip"
fedeppath="/opt/wwwroot/tob/web/democustom/fe/"
ansible $hostg -m file -a "path=$destpath state=directory recurse=yes owner=pubuser group=pubuser"
if [ $func == 'fe' ];then
    sname="/opt/deploy/pbs/scripts/democustom/deploycode.sh"
    scpname="/opt/wwwroot/deploy/democustom/deploycode.sh"
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    sh build_fe.sh $pro $cdate $tag $menv
    ansible $hostg -m shell -a "$scpname $zfile $fedeppath"
elif [ $func == 'base' ];then
    sname="/opt/deploy/pbs/scripts/democustom/deploy_be.sh"
    scpname="/opt/wwwroot/deploy/democustom/deploy_be.sh"
    img="docker.ifchange.com/projects/$pro:$cdate"    
    port=39003
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    sh build_be.sh haier $tag $cdate
    ansible $hostg -m shell -a "$scpname $pro $img $menv $port"
fi
