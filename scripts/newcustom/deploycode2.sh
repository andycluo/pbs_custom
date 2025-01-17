#!/bin/bash
if [ $# -eq 5 ];then
    deptype=$1
    zfile=$2
    destpath=$3
    pro=$4
    protype=$5
fi
if [ $protype == 'base' ];then
    destpath="$destpath/be/"
elif [ $protype == 'node' ];then
    destpath="$destpath/${pro}-node/"
elif [ $protype == 'employee' ];then
    destpath="$destpath/custom-employee/"
fi
if [ ! -d $destpath ];then
    mkdir $destpath -p
fi
if [ $protype == 'fe' -o $protype == 'employee' ];then
    sudo chown pubuser. $destpath
elif [ $protype == 'node' ];then
    echo "Node here"
else
    sudo chown pubuser. $destpath/$pro
fi
unzip -ou $zfile -d $destpath
if [ $? -ne 0 ];then
    echo 'Unpress zip failed'
    exit 400
fi
if [ $deptype == 'backend' ];then
    if [ $protype == 'base' ];then
        docker stop $pro-web
        docker start $pro-web
        if [ $? -ne 0 ];then
            echo "Start ${pro}-web failed"
            exit 400
        fi
    else
        docker stop ${pro}-${protype}
        docker start ${pro}-${protype}
        if [ $? -ne 0 ];then
            echo "Start ${pro}-${protype} failed"
            exit 400
        fi
    fi
fi
