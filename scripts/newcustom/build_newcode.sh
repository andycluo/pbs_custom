#!/bin/bash
if [ $# -eq 6 ];then
    img=$1
    pro=$2
    tag=$3
    menv=$4
    protype=$5
    otype=$6
else
    exit 400
fi

deptime=`date +'%Y%m%d%H%M'`

if [ $menv == 'pro' ];then
    menv='prod'
fi
pro_path=`echo $img|awk -F'[:.]' '{print $(NF-1)}'`
SRCROOT='/opt/deploy/coderepo/tob/custom'
SRCREPO='/opt/deploy/repo/project/tob/custom'
if [ $protype == 'fe' ];then
    SRCPATH=$SRCROOT/newfe/fe/
    REPOPATH=$SRCREPO/newfe/fe/
    CODEPATH='/opt/wwwroot/tob/web/fe/'
    DEPTYPE='front'
elif [ $protype == 'base' ];then
    SRCPATH=$SRCROOT/newbe/be/
    REPOPATH=$SRCREPO/newbase/be/
    CODEPATH='/opt/wwwroot/tob/web/custombase/'
    DEPTYPE='backend'
elif [ $protype == 'node' ];then
    SRCPATH=$SRCROOT/newnode/ifchangefe/
    REPOPATH=$SRCREPO/newnode/$pro/
    CODEPATH='/opt/wwwroot/tob/ifchangefe/'
    DEPTYPE='backend'
elif [ $protype == 'employee' ];then
    SRCPATH=$SRCROOT/common-employee/
    REPOPATH=$SRCREPO/newemployee/
    CODEPATH='/opt/wwwroot/tob/web/'
    DEPTYPE='backend'
else
    #SRCPATH=$SRCROOT/$pro/
    SRCPATH=$SRCROOT/tob-ats/
    REPOPATH=$SRCREPO/$pro/
    CODEPATH="/opt/wwwroot/tob/web/"
    DEPTYPE='backend'
fi
destpath=/opt/wwwroot/deploy/tobcustom/
CODEPAR=`dirname $SRCPATH`

function checkDir(){
    if [ ! -d $1 ];then
        mkdir $1 -p
    else
        echo "$1 aready exists"
    fi
}

function getCode(){
    code=$1
    tag=$2
    if [ ! -d $code ];then
        cd $CODEPAR;git clone $img
    fi
    cd $code;git checkout -f $tag;git pull
    if [ $? -ne 0 ];then
        echo "Update code $code  failed"
        exit 400
    fi
}

checkDir $REPOPATH
checkDir $CODEPAR
getCode  $SRCPATH $tag

zfile="${pro}-${protype}-${deptime}.zip"
if [ $protype == 'fe' ];then
    cd $REPOPATH
    for dir in assets dist
    do
        if [ $dir == 'assets' ];then
	    if [ $pro == 'talentrecommend' ];then
                rsync -avg --delete --exclude='.git/'  $SRCPATH$dir/newcommon $REPOPATH$dir/ > /dev/null 2>&1
	    else
                rsync -avg --delete --exclude='.git/'  $SRCPATH$dir/$pro $REPOPATH$dir/ > /dev/null 2>&1
	    fi
        else
            rsync -avg --delete --exclude='.git/'  $SRCPATH$dir $REPOPATH/ > /dev/null 2>&1
        fi
        if [ $? -ne 0 ];then
            echo 'Sync code be failed'
            exit 400
        fi
    done
    if [ "$otype" == 'all' ];then
        zip -r $zfile assets/$pro/$menv dist/php-views/ > /dev/null 2>&1
    else
        if [ $pro == 'talentrecommend' ];then
    	    CODEPATH='/opt/wwwroot/tob/web/democustom/fe/'
            zip -r $zfile assets/newcommon/$menv/ dist/php-views/newcommon.${menv}.html > /dev/null 2>&1
        else
            zip -r $zfile assets/$pro/$menv/ dist/php-views/${pro}.${menv}.html > /dev/null 2>&1
	fi
    fi
    if [ $? -ne 0 ];then
        echo "压缩文件失败"
        exit 400
    fi
elif [ $protype == 'node' ];then
    cd $REPOPATH
    if [ ! -d "$REPOPATH/fe" ];then
	mkdir $REPOPATH/fe -p
    fi
    rsync -avg --delete --exclude='.git/'  $SRCPATH/fe/assets/ $REPOPATH/fe/assets/ > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo 'Sync code be failed'
        exit 400
    fi
    rsync -avg --delete --exclude='.git/'  $SRCPATH/views/ $REPOPATH/views/ > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo 'Sync code be failed'
        exit 400
    fi
    zip -r $zfile fe views > /dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "压缩文件失败"
        exit 400
    fi
else
    if [ $protype == 'employee' ];then
        rsync -avg --delete --exclude='.git/'  $SRCPATH $REPOPATH/$pro/ > /dev/null 2>&1
        if [ $? -ne 0 ];then
            echo 'Sync code be failed'
            exit 400
        fi
        cd $REPOPATH
    else
        rsync -avg --delete --exclude='.git/'  $SRCPATH $REPOPATH > /dev/null 2>&1
        if [ $? -ne 0 ];then
            echo 'Sync code be failed'
            exit 400
        fi
        cd $SRCREPO 
    fi
    if [ $protype == 'ats' -o $protype == 'employee' ];then
        mkdir $pro/bootstrap/cache -p
        if [ $? -ne 0 ];then
           exit 404
        fi
    fi
    if [ $pro == 'talentrecommend' ];then
    	CODEPATH='/opt/wwwroot/tob/web/democustom/be/'
        cd $REPOPATH
        zip -r $zfile . > /dev/null 2>&1
    elif [ $pro == 'tob_custom_base' ];then
        cd /opt/deploy/repo/project/tob/custom/newbase/be
        zip -r $zfile . > /dev/null 2>&1
    else
        zip -r $zfile $pro > /dev/null 2>&1
    fi
    if [ $? -ne 0 ];then
        echo "压缩文件失败"
        exit 400
    fi
fi
scpname="/opt/wwwroot/deploy/tobcustom/deploycode2.sh"
sname="/opt/deploy/pbs_custom/scripts/newcustom/deploycode2.sh"
if [ $protype == 'fe' -o $pro == 'iflytek' -o $pro == 'jinke' -o $pro == 'customize' -o $pro == 'gcampus' -o $pro == 'visionox' -o $pro == 'webank' -o $pro == 'ka-demo' -o $pro == 'tob_custom_base' ];then
    rhost="custom_${menv}"
else
    rhost="newcustom_${menv}"
fi
ansible $rhost -m file -a "path=/opt/wwwroot/deploy/tobcustom/ state=directory recurse=yes owner=pubuser group=pubuser"
if [ $? -ne 0 ];then
    exit 400
fi
ansible $rhost -m copy -a "src=$sname dest=/opt/wwwroot/deploy/tobcustom/ owner=pubuser group=pubuser mode=0755"
if [ $? -ne 0 ];then
    exit 400
fi
ansible $rhost -m copy -a "src=$zfile dest=/opt/wwwroot/deploy/tobcustom/ owner=pubuser group=pubuser mode=0755"
if [ $? -ne 0 ];then
    exit 400
fi
zfile="/opt/wwwroot/deploy/tobcustom/$zfile"
ansible $rhost -m shell -a "$scpname  $DEPTYPE $zfile $CODEPATH $pro $protype"
if [ $? -ne 0 ];then
    exit 400
fi
