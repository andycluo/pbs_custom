#!/bin/bash
###
#sh  newdeploy.sh fe test vip master-vip 20180123

if [ $# -eq 5 ];then
    func=$1
    menv=$2
    pro=$3
    tag=$4
    cdate=$5
else
    echo 'Just build error.'
    exit
fi

if [ $func == 'fe' ];then
    if [ "x$otype" == "x" ];then
	otype='sect'
    fi
    sh build_newfe.sh $pro $cdate $tag $menv $otype
    exit 200
elif [ $func == 'base' ];then
    sh build_newbase.sh tob_custom_base $tag $cdate
elif [ $func == 'ats' ];then
    sh build_newats.sh $pro $cdate $tag $tag
fi
