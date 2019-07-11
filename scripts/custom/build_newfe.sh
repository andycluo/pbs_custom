#!/bin/bash
set -x
if [ $# -eq 5 ];then
    pro=$1
    cdate=$2
    fetag=$3
    menv=$4
    otype=$5
else
    exit 400
fi

FEPATH=/opt/deploy/coderepo/tob/custom/newfe/fe/
CPATH=/opt/deploy/repo/project/tob/custom/newfe
destpath=/opt/wwwroot/deploy/tobcustom/
DESTFE=$CPATH/fe/
CODEPAR=`dirname $FEPATH`

function checkDir(){
    if [ ! -d $1 ];then
        mkdir $1 -p
    else
        echo "$1 aready exists"
    fi
}

function getCode(){
    proname=$1
    code=$2
    tag=$3
    if [ ! -d $code ];then
        cd $CODEPAR;git clone git@192.168.1.199:web/${proname}.git
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
checkDir $DESTFE
checkDir $CODEPAR
getCode fe $FEPATH $fetag

zfile="${pro}.zip"

for dir in assets dist
do
    if [ $dir == 'assets' ];then
        rsync -avg --delete --exclude='.git/'  $FEPATH$dir/$pro $DESTFE$dir/
    else
        rsync -avg --delete --exclude='.git/'  $FEPATH$dir/ $DESTFE$dir/
    fi
    if [ $? -ne 0 ];then
        echo 'Sync code be failed'
        exit 400
    fi
done
cd $CPATH/fe
if [ -f $zfile ];then
    rm -f $zfile
fi
if [ $otype == 'all' ];then
    zip -r $zfile assets/$pro/$menv dist/php-views/
else
    zip -r $zfile assets/$pro/$menv/ dist/php-views/${pro}.${menv}.html
fi
if [ $? -ne 0 ];then
    echo "压缩文件失败"
    exit 400
fi
ansible custom_${menv} -m copy -a "src=$zfile dest=$destpath owner=pubuser group=pubuser mode=0755"
