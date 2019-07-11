#!/bin/bash
set -x
if [ $# -eq 3 ];then
    zfile=$1
    destpath=$2
    tag=$3
fi
backpath=${destpath}_${tag}_`date +'%Y%m%d%H%M'`
echo "`date +'%Y%m%d%H%M'` \t Backuping $destpath to $backpath .....\n" >> /opt/log/pbs.log
cp -a $destpath $backpath
if [ $? -ne 0 ];then
    echo "`date +'%Y%m%d%H%M'` \t Backup $destpath to $backpath  failed\n" >> /opt/log/pbs.log
    exit 400
fi
echo "`date +'%Y%m%d%H%M'` \t Backup $destpath to $backpath sucessfully\n" >> /opt/log/pbs.log
if [ ! -d $destpath ];then
    mkdir $destpath -p
fi
echo "`date +'%Y%m%d%H%M'` \t Unpressing zip $zfile ....." >> /opt/log/pbs.log
unzip -ou $zfile -d $destpath
if [ $? -ne 0 ];then
    echo "`date +'%Y%m%d%H%M'` \t Unpress zip $zfile failed" >> /opt/log/pbs.log
    exit 400
fi
echo "`date +'%Y%m%d%H%M'` \t Unpress zip $zfile sucessfully" >> /opt/log/pbs.log
rm -f $zfile
