#!/bin/bash
set -x
if [ $# -eq 2 ];then
    zfile=$1
    destpath=$2
fi
echo $zfile $destpath
if [ ! -d $destpath ];then
    mkdir $destpath -p
fi
unzip -ou $zfile -d $destpath
if [ $? -ne 0 ];then
    echo 'Unpress zip failed'
    exit 400
fi
#rm -f $zfile
