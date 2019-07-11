#!/bin/bash
set -x
if [ $# -eq 4 ];then
    pro=$1
    tag=$2
    menv=$3
    otype=$4
else
    exit 400
fi

if [ $menv = 'pro' ];then
    menv='prod'
fi
FEPATH=/opt/deploy/coderepo/tob/democustom/fe/
CPATH=/opt/deploy/repo/project/tob/democustom
destpath=/opt/wwwroot/deploy/democustom/
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
        cd $CODEPAR;git clone git@192.168.1.199:web/fe.git
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
checkDir $DESTFE
checkDir $CODEPAR
getCode fe $FEPATH $tag

zfile="${pro}.zip"

for dir in assets dist
do
    rsync -avg --delete --exclude='.git/'  $FEPATH$dir/ $DESTFE$dir/ > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo 'Sync code be failed'
        exit 400
    fi
done
cd $CPATH/fe
if [ -f $zfile ];then
    rm -f $zfile
fi
zip -r $zfile assets/newcommon/$menv dist/ assets/static/$menv > /dev/null 2>&1
if [ $? -ne 0 ];then
    echo "压缩文件失败"
    exit 400
fi

scpname="/opt/wwwroot/deploy/democustom/deploycode.sh"
sname="/opt/deploy/pbs_custom/scripts/democustom/deploycode.sh"
ansible talent_${menv} -m file -a "path=/opt/wwwroot/deploy/democustom/ state=directory recurse=yes owner=pubuser group=pubuser"
if [ $? -ne 0 ];then
    exit 400 
fi
ansible talent_${menv} -m copy -a "src=$sname dest=/opt/wwwroot/deploy/democustom/ owner=pubuser group=pubuser mode=0755"
if [ $? -ne 0 ];then
    exit 400 
fi
ansible talent_${menv} -m copy -a "src=$zfile dest=$destpath owner=pubuser group=pubuser mode=0755"
ansible talent_${menv} -m shell -a "$scpname $destpath/$zfile /opt/wwwroot/tob/web/democustom/fe/"
