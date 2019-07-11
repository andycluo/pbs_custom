#!/usr/bin/env python

import sys,os,time
from commands import getstatusoutput

log=open('/opt/log/deploy_new.log','a+')

if len(sys.argv) == 7:
    deppath=sys.argv[1]
    incfile=sys.argv[2]
    delfile=sys.argv[3]
    destpath=sys.argv[4]
    backtime=sys.argv[5]
    proname=sys.argv[6]
else:
    print "Usage: python %s  deppath incfile delfile destpath backtime" % sys.argv[0]
    sys.exit(404)
log.write('start at %s' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
backdir='/opt/backup/'+proname
backpro=backdir+'/'+backtime
os.chdir(deppath)
if not os.path.exists(backdir):
    log.write("%s Dir %s not fond.Creating it ...\n" % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),backdir))
    os.makedirs(backdir)

if os.path.exists(backpro):
    log.write('%s %s already backup to %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),proname,backpro))
else:
    cmd='cp -a %s %s/' % (destpath,backpro)
    (stat,res)=getstatusoutput(cmd)
    if not stat:
        log.write('%s Bakcup %s to %s successfully\n' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),proname,backpro))
    else:
        log.write('%s Backup %s failed\n' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),proname))
        sys.exit(400)
#del
if os.path.exists(delfile):
    for fname in eval(open(delfile,'r').read()):
        delfile=destpath+fname
        if os.path.exists(delfile):
           os.system('rm -f %s' % delfile)
           log.write('file %s deleted\n' % delfile)
else:
    log.write('%s not fond.Do not delete\n' % delfile)
#unpack
log.write('Unpackage start at %s' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
if incfile.endswith('.zip'):
    cmd='/usr/bin/unzip -uo %s -d %s/ > /dev/null' % (incfile,destpath)
else:
    cmd='/bin/tar zxf  %s -C %s/ > /dev/null' % (incfile,destpath)
(stat,res)=getstatusoutput(cmd)
if not stat:
    log.write('%s Increase code %s to %s sucessfully\n' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),incfile,destpath))
else:
    log.write('%s Increase code %s to %s failed\n' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),incfile,destpath))
    sys.exit(400)
log.write('Unpackage finished at %s' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
log.write('Finished at %s' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
