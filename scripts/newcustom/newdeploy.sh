#!/bin/bash
###
#dist全量
#sh  newdeploy.sh fe test vip master-vip all
#dist增量
#sh  newdeploy.sh fe test vip master-vip ''
#web部署
#sh newdeploy.sh base test tobcustom master-customize ''
#ats
#sh newdeploy.sh ats test vip customize-vip ''
###

declare -A atsmap
atsmap=(['vip']=39102 ['kaisagroup']=39103 ['aon']=39104)
if [ $# -eq 5 ];then
    func=$1
    menv=$2
    pro=$3
    tag=$4
    otype=$5
else
    echo 'Just build error.'
    exit
fi
cdate=`date +"%Y%m%d%H%M%S"`

hostg="custom_${menv}"
destpath="/opt/wwwroot/deploy/tobcustom/"
zfile="/opt/wwwroot/deploy/tobcustom/${pro}.zip"
fedeppath="/opt/wwwroot/tob/web/fe/"
ansible $hostg -m file -a "path=$destpath state=directory recurse=yes owner=pubuser group=pubuser"
if [ $func == 'fe' ];then
    sname="/opt/deploy/pbs/scripts/custom/deploycode.sh"
    scpname="/opt/wwwroot/deploy/tobcustom/deploycode.sh"
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    if [ "x$otype" == "x" ];then
	otype='sect'
    fi
    sh build_newfe.sh $pro $cdate $tag $menv $otype
    ansible $hostg -m shell -a "$scpname $zfile $fedeppath"
    exit 200
elif [ $func == 'base' ];then
    sname="/opt/deploy/pbs/scripts/custom/deploy2.sh"
    scpname="/opt/wwwroot/deploy/tobcustom/deploy2.sh"
    img="docker.ifchange.com/projects/tob_custom_base:$cdate"    
    port=39002
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    sh build_newbase.sh tob_custom_base $tag $cdate
    ansible $hostg -m shell -a "$scpname tob_custom_base $img $menv $port"
elif [ $func == 'ats' ];then
    sname="/opt/deploy/pbs/scripts/custom/deploy_newats.sh"
    scpname="/opt/wwwroot/deploy/tobcustom/deploy_newats.sh"
    img="docker.ifchange.com/projects/tobcustom/$pro-ats:$cdate"
    port=${atsmap[$pro]}
    ansible $hostg -m copy -a "src=$sname dest=$destpath owner=pubuser group=pubuser mode=0755"
    sh build_newats.sh $pro $cdate $tag
    ansible $hostg -m shell -a "$scpname $pro $img $menv $port"
fi

