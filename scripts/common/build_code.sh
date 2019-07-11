#!/bin/bash
set -x
if [ $# -eq 5 ];then
    giturl=$1
    pro=$2
    tag=$3
    menv=$4
    otype=$5
else
    exit 400
fi

if [ $menv == 'pro' ];then
    menv='prod'
fi
propath=`echo $giturl |awk -F'[:.]' '{print $(NF-1)}'`
profmt=`echo $propath|sed -n 's/\//_/gp'`
if [[ "$profmt" =~ ^web_.* ]];then
    propath="tob/$propath"
fi
srcPATH=/opt/deploy/coderepo/new/$propath/
repoATH=/opt/deploy/repo/project/new/$propath/
controlpath=/opt/wwwroot/deploy/common/
destpath=/opt/wwwroot/common/$propath/
CODEPAR=`dirname $srcPATH`
scpname="${destpath}deploycode.sh"
sname="/opt/deploy/pbs_custom/scripts/common/deploycode.sh"

function checkDir(){
    if [ ! -d $1 ];then
        mkdir $1 -p
    else
        echo "$1 aready exists"
    fi
}

function getCode(){
    giturl=$1
    code=$2
    tag=$3
    if [ ! -d $code ];then
        cd $CODEPAR;git clone $giturl
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}
checkDir $repoPATH
checkDir $CODEPAR
getCode $giturl $srcPATH $tag

cd $repoPATH
zfile="${pro}.zip"
if [ -f $zfile ];then
    rm -f $zfile
fi
if [ $pro == 'web_fe' ];then
    for dir in assets dist
    do
        if [ $dir == 'assets' ];then
            rsync -avg --delete --exclude='.git/'  $srcPATH$dir/$pro $repoPATH$dir/
        else
            rsync -avg --delete --exclude='.git/'  $srcATH$dir/ $repoPATH$dir/
        fi
        if [ $? -ne 0 ];then
            echo 'Sync code be failed'
            exit 400
        fi
    done
    if [ $otype == 'customall' ];then
        zip -r $zfile assets/$pro/$menv dist/php-views/
    elif [ $otype == 'all' ];then
        zip -r $zfile assets dist static
    else
        zip -r $zfile assets/$pro/$menv/ dist/php-views/${pro}.${menv}.html
    fi
else
    rsync -avg --delete --exclude='.git/'  $srcPATH/ $repoPATH/
    zip -r $zfile .
fi
if [ $? -ne 0 ];then
    echo "压缩文件失败"
    exit 400
fi
ansible common_${menv} -m file -a "path=$controlpath state=directory recurse=yes owner=pubuser group=pubuser"
if [ $? -ne 0 ];then
    exit 400
fi
ansible common_${menv} -m copy -a "src=$zfile dest=$controlpath owner=pubuser group=pubuser mode=0755"
if [ $? -ne 0 ];then
    exit 400
fi
zfile="$controlpath$zfile"
ansible common_${menv} -m shell -a "$scpname $zfile $destpath $tag"
if [ $? -ne 0 ];then
    exit 400
fi
