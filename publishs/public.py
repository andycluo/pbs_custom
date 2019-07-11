#coding:utf8

import os
import subprocess
import time
import paramiko
import logging

logger = logging.getLogger('django')

publish_log='/opt/log/be_publish.log'
f=open(publish_log,'a+')


class gitModule():
    def __init__(self,repo):
        self.repo=repo
        self.ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.result=[]
    def clone(self,codepath):
        codePar=os.path.dirname(os.path.dirname(codepath))
        if not os.path.exists(codePar):
            os.makedirs(codePar)
        os.chdir(codePar)
        cmd='git clone %s' % (self.repo)
        ret=subprocess.getstatusoutput(cmd)
        print (cmd)
        if ret and not ret[0]:
            f.write("%s\tFirst clone %s for %s" % (self.ctime,self.repo,codepath))
            return 1
        return 0
    def pull(self,dstpath):
        os.chdir(dstpath)
        ret=subprocess.getstatusoutput('git pull')
        if ret and not ret[0]:
            f.write(self.ctime+'\tUpdate successfully\n')
            return 1
        else:
            f.write('%s\tUpdate failed\n' % self.ctime)
            return 0
    def checkout(self,branch,codepath,fulltar):
        if os.path.exists(fulltar):
            os.system('rm -f %s' % fulltar)
        os.chdir(codepath)
        allcmd='git checkout -f %s' % branch
        ret = subprocess.getstatusoutput('git pull')
        if ret and not ret[0]:
            logger.info(self.ctime+'\tUpdate successfully')
        else:
            logger.error('%s\tUpdate failed\n' % self.ctime)
        self.ret = subprocess.getstatusoutput(allcmd)
        if self.ret and not self.ret[0]:
            tarcmd='tar zcf %s --exclude=.git ./' % fulltar
            logger.info(tarcmd)
            self.ret2 = subprocess.getstatusoutput(tarcmd)
            if self.ret2 and not self.ret2[0]:
                self.result.append(fulltar)
            else:
                self.result.append('')
            self.result.append('')
        return  self.result


    def diff(self, branch, lastbranch, bezip, dstpath,delfile):
        if not lastbranch:
            lastbranch = 'master'
            allcmd = 'git checkout -f master'
            incrcmd = 'git diff master remotes/origin/%s --name-only --diff-filter=AM|xargs zip %s' % (branch, bezip)
            delcmd = 'git diff master remotes/origin/%s --name-only --diff-filter=D' % (branch)
        else:
            allcmd = 'git checkout -f %s' % lastbranch
            if len(lastbranch) == 8:
                incrcmd = 'git diff remotes/origin/%s  remotes/origin/%s --name-only --diff-filter=AM|xargs zip %s' % (lastbranch, branch, bezip)
                delcmd = 'git diff remotes/origin/%s remotes/origin/%s --name-only --diff-filter=D' % (lastbranch, branch)
            else:
                incrcmd = 'git diff %s  remotes/origin/%s --name-only --diff-filter=AM|xargs zip %s' % (lastbranch, branch, bezip)
                delcmd = 'git diff %s remotes/origin/%s --name-only --diff-filter=D' % (lastbranch, branch)
        os.chdir(dstpath)
        if os.path.exists(bezip):
            os.system('rm -f %s' % bezip)
        ret0 = subprocess.getstatusoutput(allcmd)
        if not ret0:
            logger.error('checkout %s failed' % lastbranch)
        else:
            ret = subprocess.getstatusoutput('git pull')
            logger.info('%s' % str(ret))
            if ret and not ret[0]:
                logger.info(self.ctime + '\tUpdate successfully\n')
            else:
                logger.error('%s\tUpdate failed\n' % self.ctime)
        allcmd = 'git checkout -f %s' % branch
        ret = subprocess.getstatusoutput(allcmd)
        if not ret:
            self.result = []
        else:
            ret = subprocess.getstatusoutput('git pull')
            logger.info('%s' % str(ret))
            if ret and not ret[0]:
                logger.info(self.ctime + '\tUpdate successfully\n')
                upstat = 1
            else:
                logger.error('%s\tUpdate failed\n' % self.ctime)
                upstat = 0
            logger.info('1111')
            if upstat:
                logger.info(incrcmd)
                self.ret = subprocess.getstatusoutput(incrcmd)
                logger.info(self.ret)
                if self.ret and not 'Nothing to do' in self.ret[1]:
                    self.result.append(bezip)
                else:
                    return self.result
                os.chdir(dstpath)
                dellist = []
                self.ret2 = subprocess.getstatusoutput(delcmd)
                if self.ret2 and not self.ret2[0]:
                    for dpath in self.ret2[1].split('\n'):
                        dellist.append(dpath)
                else:
                    dellist=[]
                try:
                    file(delfile,'a+').write(str(dellist))
                except Exception as e:
                    print (str(e))
                self.result.append(delfile)
            else:
                self.result = []
        logger.info('ssss')
        return self.result

    def branch(self,branch,cur_baktag,dstpath):
        os.chdir(dstpath)
        cmd1='git checkout -f %s' % branch
        cmd2='git branch %s' % cur_baktag
        ret=subprocess.getstatusoutput(cmd1)
        if not ret[0]:
            ret2=subprocess.getstatusoutput(cmd2)
            if not ret2[0]:
                print ('Backup branch %s successfully' % cur_baktag)
            else:
                print ('Backup branch %s failed' % cur_baktag)
        else:
            print ('Branch %s Not Found' % branch)

def sshSync(ip,port,user,zfile,dstpath,cmd):
    ssh=paramiko.SSHClient()
    paramiko.util.log_to_file('/tmp/paramiko.log')
    #ssh.load_system_host_keys()
    #ssh.connect(ip, 22, user)
    #pkey='/root/.ssh/id_rsa'
    #pkey = '/opt/userhome/icpublish/.ssh/id_rsa'
    if ip == '211.148.28.7':
        pkey = '/etc/ic_publish.cert'
    else:
        pkey = '/home/icpublish/.ssh/id_rsa'
    print (zfile,dstpath,ip,port,cmd)
    key = paramiko.RSAKey.from_private_key_file(pkey)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,user,pkey=key)
    if zfile or dstpath:
        t=ssh.get_transport()
        sftp=paramiko.SFTPClient.from_transport(t)
        try:
            sftp.put(zfile,dstpath)
        except Exception as e:
            print (str(e))
    stdin,stdout,stderr=ssh.exec_command(cmd)
    res=stdout.readlines()
    return res[-1].strip('\n')

def codeDeploy(hosts,codepath,deppath,destpath,depfile,incfile,delfile,cur_baktime,subCodeDir):
    results={}
    cmd='ansible %s -m file -a "path=%s state=directory recurse=yes owner=pubuser group=pubuser"' % (hosts,deppath)
    print (cmd)
    (stat,res)=subprocess.getstatusoutput(cmd)
    logger.info(res)
    cmd='ansible %s -m file -a "path=%s state=directory recurse=yes owner=pubuser group=pubuser"' % (hosts,destpath)
    print (cmd)
    (stat,res)=subprocess.getstatusoutput(cmd)
    logger.info(res)
    ##sync code package
    cmd='ansible %s -m copy -a "src=%s dest=%s owner=pubuser group=pubuser mode=0755"' % (hosts,depfile,deppath)
    (stat,res)=subprocess.getstatusoutput(cmd)
    cmd='ansible %s -m copy -a "src=%s dest=%s owner=pubuser group=pubuser mode=0755"' % (hosts,codepath,deppath)
    (stat,res)=subprocess.getstatusoutput(cmd)
    print (cmd,res)
    if not stat:
        results['sync']=1
        ##unpackage
        #cmd2='ansible %s -m shell -a "%s %s %s \'%s\' %s %s %s"' % (hosts,deppath+'deploy.py',deppath,incfile,delfile,destpath,cur_baktime,subCodeDir)
        cmd2='ansible %s -m shell -a "%s %s %s \'%s\' %s %s %s"' % (hosts,deppath+'deploy.sh',deppath,incfile,delfile,destpath,cur_baktime,subCodeDir)
        logger.info(cmd2)
        (stat,res)=subprocess.getstatusoutput(cmd2)
        if not stat:
           results['deploy']=1
           logger.info(res)
        else:
           results['deploy']=0
           logger.error(res)
    else:
        results['sync']=0
        results['deploy']=0
        logger.error(res)
    return results

def dockerDeploy(group,hosts,tag,sfile,dfile,menv):
    results={}
    ##判断目录
    dpath=os.path.dirname(dfile)
    cmd='ansible %s -m file -a "path=%s state=directory recurse=yes owner=pubuser group=pubuser"' % (hosts,dpath)
    (stat,res)=subprocess.getstatusoutput(cmd)
    logger.info(res)
    ##sync script
    cmd='ansible %s -m copy -a "src=%s dest=%s owner=pubuser group=pubuser mode=0755"' % (hosts,sfile,dfile)
    (stat,res)=subprocess.getstatusoutput(cmd)
    if not stat:
        results['sync']=1
        ##Redeploy docker
        cmd2='ansible %s -m shell -a "%s %s %s %s"' % (hosts,dfile,group,tag,menv)
        logger.info(cmd2)
        (stat,res)=subprocess.getstatusoutput(cmd2)
        if not stat:
           results['deploy']=1
           logger.info(res)
        else:
           results['deploy']=0
           logger.error(res)
    else:
        results['sync']=0
        results['deploy']=0
        logger.error(res)
    return results

def customDeploy(proname,hosts,tag,sfile,dfile,menv,port):
    results={}
    ##判断目录
    dpath=os.path.dirname(dfile)
    cmd='ansible %s -m file -a "path=%s state=directory recurse=yes owner=pubuser group=pubuser"' % (hosts,dpath)
    (stat,res)=subprocess.getstatusoutput(cmd)
    logger.info(res)
    ##sync script
    cmd='ansible %s -m copy -a "src=%s dest=%s owner=pubuser group=pubuser mode=0755"' % (hosts,sfile,dfile)
    (stat,res)=subprocess.getstatusoutput(cmd)
    if not stat:
        results['sync']=1
        ##Redeploy docker
        cmd2='ansible %s -m shell -a "%s %s %s %s %s"' % (hosts,dfile,proname,tag,menv,port)
        logger.info(cmd2)
        (stat,res)=subprocess.getstatusoutput(cmd2)
        if not stat:
           results['deploy']=1
           logger.info(res)
        else:
           results['deploy']=0
           logger.error(res)
    else:
        results['sync']=0
        results['deploy']=0
        logger.error(res)
    return results


def diffConf(newdata,olddata):
    res={'mod':{},'add':{},'del':{}}
    for key in newdata.keys():
        if key in olddata.keys():
            if newdata[key] != olddata[key]:
                res['mod'][key]=newdata[key]
            else:
                continue
        else:
            res['add'][key]=newdata[key]
    for key in olddata.keys():
         if key not in newdata.keys():
             res['del'][key]=olddata[key]
    return res
