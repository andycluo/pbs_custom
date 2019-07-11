#!/bin/bash


logpath="/opt/log/deploy_new.log"

if [ $# -eq 6 ];then
    deppath=$1
    incfile=$2
    delfile=$3
    destpath=$4
    backtime=$5
    proname=$6
else
   echo "Usage: sh $0  deppath incfile delfile destpath backtime" 
   exit 404
fi

echo `date +"%Y-m%-%d %H:%M:%S"` >> $logpath
backdir="/opt/backup/$proname"
backpro="$backdir/$backtime"
cd $deppath
if [ ! -d $backdir ];then
    echo "`date +"%Y-m%-%d %H:%M:%S"` Dir $backdir not fond.Creating it ...\n" >> $logpath
    mkdir $backdir -p
fi

if [ -d $backpro ];then
    echo "`date +\"%Y-m%-%d %H:%M:%S\"` $proname  already backup to $backpro\n" >> $logpath
else:
    cp -a $destpath $backpro
    if [ $? -eq 0 ];then
        echo "`date +\"%Y-m%-%d %H:%M:%S\"` $proname Bakcup  to $backpro successfully\n" >> $logpath
    else:
        echo "`date +\"%Y-m%-%d %H:%M:%S\"` Backup $proname failed\n" >> $logpath
        exit 400
    fi
fi
##del
#if [ -f $delfile ];then
#    for fname in eval(open(delfile,'r').read()):
#        delfile=destpath+fname
#        if os.path.exists(delfile):
#           os.system('rm -f %s' % delfile)
#           log.write('file %s deleted\n' % delfile)
#else:
#    log.write('%s not fond.Do not delete\n' % delfile)

#unpack
echo "Unpackage start at `date +\"%Y-m%-%d %H:%M:%S\"`" >> $logpath
pre=${incfile##*.}
if [ $pre == 'zip' ];then
    /usr/bin/unzip -uo $incfile -d $destpath/ > /dev/null
else
    /bin/tar zxf  $incfile -C $destpath/ > /dev/null
fi
if [ $? -eq 0 ];then
    echo "`date +\"%Y-m%-%d %H:%M:%S\"`  Increase code $incfile to $destpath sucessfully\n" >> $logpath
else
    echo "`date +\"%Y-m%-%d %H:%M:%S\"` Increase code $incfile to $destpath failed\n" >> $logpath
    exit 400
fi
echo "Unpackage finished at `date +\"%Y-m%-%d %H:%M:%S\"`" >> $logpath
echo "Finished at `date +\"%Y-m%-%d %H:%M:%S\"`" >> $logpath
