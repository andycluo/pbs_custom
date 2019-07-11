#coding:utf8
from publishs.models import *
from publishs.public import *
from django.shortcuts import HttpResponse
import time,os
import subprocess
import json
import logging

logger = logging.getLogger('django')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

promaps={
    'tob_custom_base':39002,
    'greentown':39101,
    'kaisagroup':39103,
    'aon':39104,
    'gcampus':39105,
    'icampus':39106,
    'iflytek':39107,
    'jinke':39108,
    'ka-demo':39109,
    'webank':39110,
    'visionox':39111,
    'vanke':39112,
    'cifi':39113,
    'zotye':39114,
    'jianye':39115,
    'shimao':39116,
    'pharmablock':39117,
    'wicresoft':39118,
    'brc':39119,
    'logan':39120,
    'ka-demo-node':39209,
    'ka-demo-employee':39309,
    'talentrecommend':39003,
    'logan-node':39220,
    'jianye-node':39221,
}

def aaa(request):
	datas = request.POST
	print (datas['pbstat'])
	return HttpResponse(json.dumps({"stat":"0", "info":"没有需要同步的tag"}))

def rollback(request):
    if request.method == 'POST':
        print ('%s  Rollback start.....' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        datas = request.POST
        tag_env = datas['tenv'].strip()
        branchname = datas['tagbranch'].strip()
        proname = datas['proname'].strip().replace('_','/')
        lasttag = datas['lasttag'].strip()
        tagid = datas['tagid']
        if tag_env == 'test':
            host = '211.148.28.19'
            port = 68
            user = 'icpublish'
        else:
            host = '211.148.28.7'
            port = 22118
            user = 'icpublish'
        res = sshSync(host, port, user,'','','/usr/bin/python /opt/userhome/icpublish/deploy2.py rollback %s %s' % (proname, lasttag))
        res='finish'
        if 'finish' in res and not 'failed' in res:
            msg = {"stat": "1", "info": "%s(%s)回滚到%s完成" % (proname,tag_env,lasttag)}
            cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if tag_env == 'online':
                Tagconf.objects.filter(tag_branch=branchname, id=tagid,pro_name=proname).update(published_at=cur_time)
            else:
                Tagconf.objects.filter(tag_branch=branchname, id=tagid,pro_name=proname).update(t_published_at=cur_time)
        else:
            msg = {"stat": "0", "info": "%s(%s)回滚到%s失败" %  (proname,tag_env,lasttag)}
        print ('%s  Rollback finished' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    return HttpResponse(json.dumps(msg), content_type='application/json')


def asynctag(request):
    if request.method == 'POST':
        print ('%s  Start sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        datas = request.POST
        tag_env = datas['genv'].strip()
        logger.info(tag_env)
        branch=datas['tagbranch'].strip()
        stat=datas['stat']
        tagid=datas['tagid']
        if datas.has_key('pbstat') and datas['pbstat'] == '1':
            pbstat = 1
        else:
            pbstat = 0
        if tag_env == 'test':
            host = '211.148.28.19'
            port = 68
            user = 'icpublish'
            sstat = 1
        else:
            host = '211.148.28.7'
            port = 22118
            user = 'icpublish'
            sstat = 2
        syncstat = 0
        if stat:
            syncstat = 1
        ##获取当前配置
        if syncstat:
            db = Tagconf.objects.filter(id=tagid)
            print (db.values())
            if not db.values():
                datas = {}
                msg={'stat':'0','info':'Not found'}
            else:
                for sect in db.values():
                    tagurl = sect['tag_url']
                    branch = sect['tag_branch']
                    if 'pro_name' in sect.keys():
                        pro_name=sect['pro_name']
                    else:
                        pro_name=tagurl.split(':')[1].split('.')[0].replace('/','_')
                    created_at = sect['created_at']
                    if  tag_env == 'test' or tag_env == 'test3':
                        lpubtag=sect['t_last_published_tag']
                    else:
                        lpubtag=sect['last_published_tag']
                    print (lpubtag)
                    codeParDir = '/opt/deploy/code/' + tagurl.split(':')[1].split('.')[0].split('/')[0]
                    codeDir = tagurl.split(':')[1].split('.')[0]
                    codepath = '/opt/deploy/code/' + codeDir
                    print (pro_name)
                    cur_date = time.strftime('%Y-%m-%d', time.localtime())
                    cur_baktime = time.strftime('%Y%m%d%H%M', time.localtime())
                    fulltar = '/opt/zipdir/%s_full_%s.tar.gz' % (pro_name,cur_date)
                    bezip = '/opt/zipdir/%s_incr_%s.zip' % (pro_name,cur_date)
                    git = gitModule(tagurl)
                    print (codeParDir)
                    if not os.path.exists(codeParDir):
                        cmd='mkdir -p ' + codeParDir
                        print (cmd)
                        os.system(cmd)
                        stat,res=subprocess.getstatusoutput('ls '+codeParDir)
                        print (stat,res)
                    if not os.path.exists(codepath):
                        git.clone(codepath)
                        msg = {"stat":"1", "info":''}
                        print (msg)
                    if 'master' in branch:
                        dstpath = '/opt/zipdir/%s_full_%s.tar.gz' % (pro_name,cur_date)
                        print (dstpath)
                        delfiles = ['']
                        ret = git.checkout('master', codepath, fulltar)
                        if ret:
                            git.branch(branch, cur_baktime,codepath)
                            res = sshSync(host, port, user, fulltar, dstpath,
                                              '/usr/bin/python /opt/userhome/icpublish/deploy2.py deploy %s %s "%s" %s' % (
                                              codeDir, fulltar, delfiles, cur_baktime))
                            print (res)
                            if 'finish' in res and not 'failed' in res:
                                cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                try:
                                    stat=Tagconf.objects.filter(id=tagid).values('status')
                                    print (stat)
                                    #if tag_env == 'test':
                                    #    db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,
                                    #             pro_name=pro_name, status=sstat, created_at=created_at,
                                    #             )
                                    #    db.save()
                                except Exception as e:
                                    print (str(e))
                                if tag_env == 'online':
                                    Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch).update(status=sstat, tag_env='online')
                                    Tagconf.objects.filter(id=tagid).update(published_at=cur_time,last_published_tag=cur_baktime)
                                else:
                                    Tagconf.objects.filter(id=tagid).update(status=sstat,t_published_at=cur_time,t_last_published_tag=cur_baktime)
                                    if tag_env == 'test':
                                        db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,
                                                 pro_name=pro_name, status=sstat, created_at=created_at,
                                                 )
                                        db.save()
                                tmpdata=Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch,tag_env=tag_env).order_by('-id').values()[0]
                                msg={"stat":"1","info":"同步成功",'id':tmpdata['id']}
                            else:
                                msg={"stat":"0","info":"同步失败",'id':tagid}
                        else:
                            msg = {"stat":"0", "info":"获取全量文件失败",'id':tagid}
                        #return msg
                        print (msg)
                    else:
                        print (lpubtag,'ssssssssssssssssss')
                        if pbstat:
                            dstpath = '/opt/zipdir/%s_full_%s.tar.gz' % (pro_name, cur_date)
                            rets = git.checkout(branch, codepath, fulltar)
                            lasttag = 0
                            logger.info('dog'+str(lasttag))
                        elif lpubtag:
                            dstpath = '/opt/zipdir/%s_incr_%s.zip' % (pro_name,cur_date)
                            rets = git.diff(branch, lpubtag, bezip, codepath)
                            lasttag = lpubtag
                            logger.info('monkey'+lasttag)
                        else:
                            try:
                                if tag_env == 'test':
                                    status=1
                                    pubat='-t_published_at'
                                    tag='t_last_published_tag'
                                    datas = Tagconf.objects.exclude(t_last_published_tag = '').filter(tag_url=tagurl).order_by('-t_published_at').values()
                                else:
                                    status=2
                                    pubat='-published_at'
                                    tag='last_published_tag'
                                    datas = Tagconf.objects.exclude(last_published_tag = '').filter(tag_url=tagurl).order_by('-published_at').values()
                                #datas = Tagconf.objects.filter(tag_env=tag_env, status=status, tag_url=tagurl).order_by(
                                #    pubat).values()
                                logger.info("%s\t %s\t" % (str(datas),tag))
                                if datas:
                                    print (datas[0])
                                    lasttag = datas[0][tag]
                                else:
                                    lasttag = 0
                            except Exception as e:
                                logger.error(str(e))
                                lasttag = 0
                            logger.info(lasttag,pbstat,tag,'gggggggggggggggggg')
                            if lasttag and not pbstat:
                                dstpath = '/opt/zipdir/%s_incr_%s.zip' % (pro_name, cur_date)
                                rets = git.diff(branch, lasttag, bezip, codepath)
                                logger.info("%s\t%s\telephant" % (lasttag,pbstat))
                            else:
                                dstpath = '/opt/zipdir/%s_full_%s.tar.gz' % (pro_name, cur_date)
                                rets = git.checkout(branch, codepath, fulltar)
                                logger.info("%s\t%s\tmouse" % (lasttag,pbstat))
                        logger.info(str(rets)+'lllllllllll')
                        if rets:
                            print (cur_baktime,'qqqqqqq')
                            git.branch(branch, cur_baktime,codepath)
                            if lasttag and not pbstat:
                                incrfile = rets[0]
                                delfiles = rets[1]
                                print ('fffffff')
                                if incrfile:
                                    res = sshSync(host, port, user, incrfile, dstpath,'/usr/bin/python /opt/userhome/icpublish/deploy2.py deploy %s %s "%s" %s' % (codeDir, incrfile, delfiles, cur_baktime))
                                    if 'finish' in res and not 'failed' in res:
                                        pub_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                        print (created_at,pub_time,cur_baktime)
                                        try:
                                            stat = Tagconf.objects.filter(tag_branch=branch, id=tagid).values('status')
                                            print (stat)
                                            if tag_env == 'test':
                                                db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,
                                                         pro_name=pro_name, status=sstat, created_at=created_at
                                                    )
                                                db.save()
                                        except Exception as e:
                                            print ('mmmmmmmmmmmmmm')
                                            print (str(e))
                                        print ('ppppppppppp',cur_baktime,tag_env)
                                        if tag_env == 'online':
                                            Tagconf.objects.filter(tag_branch=branch).update(status=sstat, tag_env='online')
                                            Tagconf.objects.filter(tag_branch=branch,id=tagid).update(published_at=pub_time,last_published_tag=cur_baktime)
                                        else:
                                            Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,t_published_at=pub_time,t_last_published_tag=cur_baktime)
                                        tmpdata=Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch,tag_env=tag_env).order_by('-id').values()[0]
                                        msg = {"stat":"1", "info":"同步完成",'id':tmpdata['id']}
                                    else:
                                        msg = {"stat":"0", "info":"同步失败",'id':tagid}
                            else:
                                delfiles = ['']
                                res = sshSync(host, port, user, fulltar, dstpath,
		                                     '/usr/bin/python /opt/userhome/icpublish/deploy2.py deploy %s %s "%s" %s' % (
		                                      codeDir, fulltar, delfiles, cur_baktime))
                                print (res)
                                if 'finish' in res and not 'failed' in res:
                                    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                    print ('sss'+str(sstat))
                                    try:
                                        stat = Tagconf.objects.filter(tag_branch=branch, id=tagid).values('status')
                                        print (stat)
                                        if tag_env == 'test':
                                            db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,
                                                     pro_name=pro_name, status=sstat, created_at=created_at,
                                                     )
                                            db.save()
                                    except Exception as e:
                                        print (str(e))
                                    print ('fffffffff',cur_baktime,tag_env)
                                    if tag_env == 'online':
                                        Tagconf.objects.filter(tag_branch=branch).update(status=sstat, tag_env='online')
                                        Tagconf.objects.filter(tag_branch=branch,id=tagid).update(published_at=cur_time,last_published_tag=cur_baktime)
                                    else:
                                        Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,t_published_at=cur_time,t_last_published_tag=cur_baktime)
                                    tmpdata=Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch,tag_env=tag_env).order_by('-id').values()[0]
                                    msg = {"stat":"1", "info":"同步完成",'id':tmpdata['id']}
                                else:
                                    msg = {"stat":"0", "info":"同步失败",'id':tagid}
                        else:
                            msg = {"stat":"1", "info":"没有增量文件可更新",'id':tagid}
        else:
            msg = {"stat":"1", "info":"没有需要同步的tag"}
    print ('%s  End sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    return HttpResponse(json.dumps(msg),content_type='application/json')

def asynctag2(request):
    if request.method == 'POST':
        logger.info('%s  Start sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        datas = request.POST
        logger.info(datas)
        tag_env = datas['genv'].strip()
        branch=datas['tagbranch'].strip()
        stat=datas['stat']
        tagid=datas['tagid']
        if datas.has_key('pbstat') and datas['pbstat'] == '1':
            pbstat = 1
        else:
            pbstat = 0
        if tag_env == 'testing2':
            sstat = 1
        elif tag_env == 'testing3':
            sstat = 3
        else:
            sstat = 2

        syncstat = 0
        if stat:
            syncstat = 1
        logger.info(str(syncstat)+tag_env)
        ##获取当前配置
        if syncstat:
            db = Tagconf.objects.filter(id=tagid)
            print (db.values())
            if not db.values():
                datas = {}
                msg={'stat':'0','info':'Not found'}
            else:
                codeDir='/opt/deploy/coderepo/'
                repoDir='/opt/deploy/repo/project/'
                depDir='/opt/wwwroot/deploy/'
                destDir='/opt/wwwroot/'
                for sect in db.values():
                    tagurl = sect['tag_url']
                    branch = sect['tag_branch']
                    if 'pro_name' in sect.keys():
                        pro_name=sect['pro_name']
                    else:
                        pro_name=tagurl.split(':')[1].split('.')[0].replace('/','_')
                    created_at = sect['created_at']
                    if  tag_env == 'testing2':
                        lpubtag=sect['t_last_published_tag']
                    elif  tag_env == 'testing3':
                        lpubtag=sect['t3_last_published_tag']
                    else:
                        lpubtag=sect['last_published_tag']
                    logger.info("datas: %s\ttag_env: %s\tlast_tag: %s" % (sect,tag_env,lpubtag))
                    subCodeDir = tagurl.split(':')[1].split('.')[0]
                    print (pro_name)
                    if 'dz-' in pro_name or pro_name == 'web_fe':
                        pro = 'fe'
                    else:
                        pro = pro_name.split('/')[-1]
                    hosts = pro+'_'+tag_env
                    cur_date = time.strftime('%Y-%m-%d', time.localtime())
                    cur_date2 = time.strftime('%Y%m%d%H%M', time.localtime())
                    cur_baktime = time.strftime('%Y%m%d%H%M', time.localtime())
                    backBranch = pro_name+'-'+cur_baktime
                    print (codeDir)
                    if pro_name.startswith('web_'):
                        codepath = codeDir + 'tob/' + pro +'/'
                        repopath = repoDir + 'tob/' + pro +'/'+ cur_date2 + '/'
                        deppath  = depDir + pro + '/'
                        if tag_env == 'testing3':
                            destpath = destDir + 'tob/web/' + pro + '_test3/'
                        else:
                            destpath = destDir + 'tob/web/' + pro + '/'
                        #depfile = '/opt/deploy/pbs/scripts/'+pro+'/deploy.py'
                        depfile = '/opt/deploy/pbs/scripts/'+pro+'/deploy.sh'
                    else:
                        codepath = codeDir + subCodeDir + '/'
                        repopath = repoDir + subCodeDir + '/' + cur_date2 + '/'
                        deppath  = depDir + subCodeDir + '/'
                        destpath = destDir + subCodeDir + '/'
                        #depfile = '/opt/deploy/pbs/scripts/'+subCodeDir+'/deploy.py'
                        depfile = '/opt/deploy/pbs/scripts/'+subCodeDir+'/deploy.sh'
                    if not os.path.exists(repopath):
                        os.makedirs(repopath)
                    depscript = os.path.dirname(depfile)
                    if not os.path.exists(depscript):
                        os.makedirs(depscript)
                    print (depfile)
                    fulltar = '%s%s_full.tar.gz' % (repopath,pro_name)
                    bezip = '%s%s_incr.zip' % (repopath,pro_name)
                    delfile = '%s%s_del' % (repopath,pro_name)
                    git = gitModule(tagurl)
                    print ('aaaaaa',codepath)
                    if not os.path.exists(codepath):
                        git.clone(codepath)
                        msg = {"stat":"1", "info":''}
                        print (msg)
                    logger.info("%s\t%s" % ('ddddd',branch))
                    if 'master' in branch:
                        ret = git.checkout('master', codepath, fulltar)
                        if ret:
                            git.branch(branch, backBranch,codepath)
                            res = codeDeploy(hosts,repopath,deppath,destpath,depfile,'','',cur_baktime,subCodeDir)
                            print (res)
                            if res['sync'] and res['deploy']:
                                cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                try:
                                    stat=Tagconf.objects.filter(id=tagid).values('status')
                                    print (stat)
                                except Exception as e:
                                    print (str(e))
                                if tag_env == 'online':
                                    Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch).update(status=sstat, tag_env='online')
                                    Tagconf.objects.filter(id=tagid).update(published_at=cur_time,last_published_tag=backBranch)
                                elif tag_env == 'testing3':
                                    Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch).update(status=sstat, tag_env='testing3')
                                    Tagconf.objects.filter(id=tagid).update(status=sstat,t3_published_at=cur_time,t3_last_published_tag=backBranch)
                                else:
                                    Tagconf.objects.filter(id=tagid).update(status=sstat,t_published_at=cur_time,t_last_published_tag=backBranch)
                                if tag_env == 'testing2' or tag_env == 'testing3':
                                    db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,
                                             pro_name=pro_name, status=sstat, created_at=created_at,
                                             )
                                    db.save()
                                tmpdata=Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch,tag_env=tag_env).order_by('-id').values()[0]
                                msg={"stat":"1","info":"同步成功",'id':tmpdata['id']}
                            else:
                                msg={"stat":"0","info":"同步失败",'id':tagid}
                        else:
                            msg = {"stat":"0", "info":"获取全量文件失败",'id':tagid}
                        #return msg
                        print (msg)
                        logger.info(str(msg))
                    else:
                        logger.info(str(lpubtag)+'\tssssssssssssssssss')
                        if pbstat:
                            rets = git.checkout(branch, codepath, fulltar)
                            lasttag = 0
                            logger.info('dog')
                        elif lpubtag:
                            rets = git.diff(branch, lpubtag, bezip, codepath,delfile)
                            lasttag = lpubtag
                            logger.info('monkey')
                        else:
                            try:
                                if tag_env == 'testing2':
                                    status=1
                                    pubat='-t_published_at'
                                    tag='t_last_published_tag'
                                    datas = Tagconf.objects.exclude(t_last_published_tag = '').filter(tag_url=tagurl).order_by('-t_published_at').values()
                                elif tag_env == 'testing3':
                                    status=3
                                    pubat='-t3_published_at'
                                    tag='t3_last_published_tag'
                                    datas = Tagconf.objects.exclude(t3_last_published_tag = '').filter(tag_url=tagurl).order_by('-t3_published_at').values()
                                elif tag_env == 'online':
                                    status=2
                                    pubat='-published_at'
                                    tag='last_published_tag'
                                    datas = Tagconf.objects.exclude(last_published_tag = '').filter(tag_url=tagurl).order_by('-published_at').values()
                                if datas:
                                    print (datas[0])
                                    lasttag = datas[0][tag]
                                else:
                                    lasttag = 0
                            except Exception as e:
                                print (str(e))
                                lasttag = 0
                            logger.info("%s\t%s\t%s\t%s" % (lasttag,pbstat,tag,'gggggggggggggggggg'))
                            if lasttag and not pbstat:
                                rets = git.diff(branch, lasttag, bezip, codepath,delfile)
                                print ('elephant')
                            else:
                                rets = git.checkout(branch, codepath, fulltar)
                                print (rets)
                                print ('mouse')
                        logger.info(rets)
                        logger.info('llllllllll')
                        if rets:
                            print (backBranch,'qqqqqqq')
                            git.branch(branch, backBranch,codepath)
                            incrfile = os.path.basename(rets[0]) if rets[0] else ''
                            delfile = os.path.basename(rets[1]) if rets[1] else ''
                            if lasttag and not pbstat:
                                print ('fffffff',lasttag)
                                if incrfile:
                                    res = codeDeploy(hosts,repopath,deppath,destpath,depfile,incrfile,delfile,cur_baktime,subCodeDir)
                                    if res['sync'] and res['deploy']:
                                        pub_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                        print (created_at,pub_time,cur_baktime)
                                        try:
                                            stat = Tagconf.objects.filter(tag_branch=branch, id=tagid).values('status')
                                            print (stat)
                                            logger.info('%s\t%s\t%s' % (branch,tag_env,sstat))
                                            if tag_env == 'testing2' or tag_env == 'testing3':
                                                db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,pro_name=pro_name, status=sstat, created_at=created_at)
                                                db.save()
                                        except Exception as e:
                                            print ('mmmmmmmmmmmmmm')
                                            print (str(e))
                                        print ('ppppppppppp',backBranch,tag_env)
                                        if tag_env == 'online':
                                            Tagconf.objects.filter(tag_branch=branch).update(status=sstat, tag_env='online')
                                            Tagconf.objects.filter(tag_branch=branch,id=tagid).update(published_at=pub_time,last_published_tag=backBranch)
                                        elif tag_env == 'testing3':
                                            Tagconf.objects.filter(tag_branch=branch).update(status=sstat, tag_env='testing3')
                                            Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,t3_published_at=pub_time,t3_last_published_tag=backBranch)
                                        else:
                                            Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,t_published_at=pub_time,t_last_published_tag=backBranch)
                                        tmpdata=Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch,tag_env=tag_env).order_by('-id').values()[0]
                                        msg = {"stat":"1", "info":"同步完成",'id':tmpdata['id']}
                                    else:
                                        msg = {"stat":"0", "info":"同步失败",'id':tagid}
                            else:
                                print ('fuck')
                                try:
                                    res = codeDeploy(hosts,repopath,deppath,destpath,depfile,incrfile,delfile,cur_baktime,subCodeDir)
                                except Exception as e:
                                    print (str(e))
                                print ('fuck2')
                                print (res)
                                if res['sync'] and res['deploy']:
                                    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                    print ('sss'+str(sstat))
                                    try:
                                        stat = Tagconf.objects.filter(tag_branch=branch, id=tagid).values('status')
                                        print (stat)
                                        if tag_env == 'testing2' or tag_env == 'testing3':
                                            db = Tagconf(tag_url=tagurl, tag_branch=branch, tag_env=tag_env,
                                                     pro_name=pro_name, status=sstat, created_at=created_at,
                                                     )
                                            db.save()
                                    except Exception as e:
                                        print (str(e))
                                    print ('fffffffff',cur_baktime,tag_env)
                                    if tag_env == 'online':
                                        Tagconf.objects.filter(tag_branch=branch).update(status=sstat, tag_env='online')
                                        Tagconf.objects.filter(tag_branch=branch,id=tagid).update(published_at=cur_time,last_published_tag=backBranch)
                                    elif tag_env == 'testing3':
                                        Tagconf.objects.filter(tag_branch=branch).update(status=sstat, tag_env='testing3')
                                        Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,t3_published_at=cur_time,t3_last_published_tag=backBranch)
                                    else:
                                        Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,t_published_at=cur_time,t_last_published_tag=backBranch)
                                    tmpdata=Tagconf.objects.filter(tag_url=tagurl,tag_branch=branch,tag_env=tag_env).order_by('-id').values()[0]
                                    msg = {"stat":"1", "info":"同步完成",'id':tmpdata['id']}
                                else:
                                    msg = {"stat":"0", "info":"同步失败",'id':tagid}
                        else:
                            msg = {"stat":"1", "info":"没有增量文件可更新",'id':tagid}
        else:
            msg = {"stat":"1", "info":"没有需要同步的tag"}
    print ('%s  End sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    return HttpResponse(json.dumps(msg),content_type='application/json')

def buildimg(request):
    if request.method == 'POST':
        datas = request.POST
        tsign=datas['tagsign']
        pro_name=datas['proname']
        pro_type=datas['protype']
        ftag=datas['febranch']
        btag=datas['bebranch']
        logger.info("%s Building image %s ...." % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),pro_name))
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        tag = time.strftime('%Y%m%d%H%M', time.localtime())
        script = os.path.join(BASE_DIR,'scripts/%s/build.sh' % pro_name)
        if pro_type == 1:
            cmd='%s %s %s %s' % (script,pro_name,tag,btag)
        else:
            cmd='%s %s %s %s %s' % (script,pro_name,tag,btag,ftag)
        logger.info(cmd)
        if pro_type == '3':
            dockerimg='docker.ifchange.com/app/%s:%s' % (pro_name,tag)
        else:
            dockerimg='docker.ifchange.com/projects/%s:%s' % (pro_name,tag)
        logger.info(dockerimg+str(type(pro_type)))
        try:
            (stat,res)=subprocess.getstatusoutput(cmd)
            if not stat:
                Docker.objects.filter(pro_sign=tsign).update(build_stat=1,build_at=cur_time,dockerimg=dockerimg,deploy_stat=0)
                db=BuildHistory(build_sign=tsign,build_tag=tag,build_at=cur_time)
                db.save()
                err=[0,'构建成功']
                logger.info('构建成功'+str(res))
            else:
                Docker.objects.filter(pro_sign=tsign).update(build_stat=2,build_at=cur_time,deploy_stat=0)
                err=[1,'构建失败']
                logger.error('构建失败！！！'+res+'\t'+cmd)
        except Exception as e:
            Docker.objects.filter(pro_sign=tsign).update(build_stat=2,build_at=cur_time)
            err=[1,str(e)]
            logger.error(str(e))
        stats=Docker.objects.filter(pro_sign=tsign).values()[0]['build_stat']
        msg={'stat':stats,'err':err}
    else:
        msg={'stat':1,'err':'不支持的方式'}
        logger.error('不支持的方式')
    return HttpResponse(json.dumps(msg),content_type='application/json')

def asyncdocker(request):
    if request.method == 'POST':
        logger.info('%s  Start sync docker .....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        datas = request.POST
        tag_env = datas['genv'].strip()
        branch=datas['tagbranch'].strip()
        stat=datas['stat']
        tagid=datas['tagid']
        ##获取当前配置
        db = Docker.objects.filter(pro_sign=tagid,build_stat=1,is_delete=0)
        if not db.values():
            datas = {}
            msg={'stat':'0','info':'Not found'}
            logger.error('没有找到相应配置')
        else:
            sect=db.values().values()[0]
            groups=sect['pro_name']
            hosts=groups+'_'+tag_env
            tag=sect['dockerimg']
            sfile=os.path.join(BASE_DIR,'scripts/%s/deploy.sh' % groups)
            dfile='/opt/wwwroot/deploy/%s/deploy.sh' % groups
            res=dockerDeploy(groups,hosts,tag,sfile,dfile,tag_env)
            if not res['sync']:
                errCode=1
                info=u'同步脚本失败'
                logger.error('同步脚本失败')
            elif not res['deploy']:
                errCode=1
                info=u'部署docker失败'
                logger.error('部署docker失败')
            else:
                errCode=0
                info=u'部署成功'
                logger.info('部署成功')
    else:
        errCode=1
        info=u'不支持的请求方式'
        logger.error('不支持的请求方式')
    if tag_env == 'test' or tag_env == 'testing2':
        deploy_ok=1
        deploy_err=3
    elif tag_env == 'testing3'  or tag_env == 'test3' :
        deploy_ok=5
        deploy_err=6
    else:
        deploy_ok=2
        deploy_err=4
    print (errCode)
    if errCode:
        Docker.objects.filter(pro_sign=tagid).update(deploy_stat=deploy_err)
    else:
        Docker.objects.filter(pro_sign=tagid).update(deploy_stat=deploy_ok)
    results={'stat':errCode,'msg':info}
    print (results)
    logger.info('%s  End sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    return HttpResponse(json.dumps(results),content_type='application/json')

def asynccustomfe(request):
    typedict={'1':'fe','2':'base','3':'ats','4':'node','5':'employee'}
    if request.method == 'POST':
        logger.info('%s  Start sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        datas = request.POST
        logger.info(datas)
        pro_name = datas['proname'].strip()
        tag_env = datas['genv'].strip()
        tagurl = datas['tagurl'].strip()
        branch=datas['tagbranch'].strip()
        stat=datas['stat']
        tagid=datas['tagid']
        protype=typedict[datas['protype']]
        if datas.has_key('pbstat') and datas['pbstat'] == '1':
            pbstat = 1
        else:
            pbstat = 0
            syncstat = 0
        if stat:
            syncstat = 1
        if pro_name == '定制base':
            pro_name='tob_custom_base'
        logger.info(str(syncstat)+tag_env)
        ##获取当前配置
        if syncstat:
            if pbstat:
                otype='all'
        else:
            otype=''
            try:
                if tag_env == 'test':
                    datas = CustomPro.objects.filter(tag_url=tagurl,tag_env=1).order_by('-published_at').values()
                elif tag_env == 'pro':
                    datas = CustomPro.objects.filter(tag_url=tagurl,tag_env=2).order_by('-published_at').values()
            except Exception as e:
                logger.error(str(e))
                pass
            if pro_name in ['talentrecommend']:
                cmd="/opt/deploy/pbs_custom/scripts/democustom/build_fe.sh %s %s %s '%s'" % (pro_name,branch,tag_env,otype)
            else:
                cmd="/opt/deploy/pbs_custom/scripts/newcustom/build_newcode.sh %s %s %s %s %s '%s'" % (tagurl,pro_name,branch,tag_env,protype,otype)
            #cmd="/opt/deploy/pbs_custom/scripts/newcustom/build_newcode.sh %s %s %s %s %s '%s'" % (tagurl,pro_name,branch,tag_env,protype,otype)
            logger.info(cmd)
            (stat,res)=subprocess.getstatusoutput(cmd)
            logger.info('%s %s' % (stat,res))
            cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if not stat:
                print ('fffff')
                if tag_env == 'pro':
                    CustomPro.objects.filter(id=tagid).update(deploy_stat=2, tag_env=2,published_at=cur_time)
                else:
                    CustomPro.objects.filter(id=tagid).update(deploy_stat=1,published_at=cur_time)
                msg = {"stat":"1", "info":"同步完成",'id':tagid}
            else:
                if tag_env == 'pro':
                    CustomPro.objects.filter(id=tagid).update(deploy_stat=4, tag_env=2,published_at=cur_time)
                else:
                    CustomPro.objects.filter(id=tagid).update(deploy_stat=3,published_at=cur_time)
                msg = {"stat":"0", "info":"同步失败",'id':tagid}
    else:
            msg = {"stat":"1", "info":"没有需要同步的tag"}
    logger.info(msg['info'])
    logger.info('%s  End sync %s to %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),pro_name,tag_env))
    logger.info(str(msg))
    return HttpResponse(json.dumps(msg),content_type='application/json')

def buildcustom(request):
    if request.method == 'POST':
        datas = request.POST
        tsign=datas['tagsign']
        pro_name=datas['proname']
        pro_type=datas['protype']
        branch=datas['codebranch']
        logger.info("%s Building image %s ...." % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),pro_name))
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        tag = time.strftime('%Y%m%d%H%M', time.localtime())
        script = os.path.join(BASE_DIR,'scripts/%s/build.sh' % pro_name)
        if pro_type == '2':
            if pro_name in ['talentrecommend']:
                cmd='%s %s %s' % (os.path.join(BASE_DIR,'scripts/democustom/build_be.sh'),pro_name,tag)
            else:
                pro_name='tob_custom_base'
                cmd='%s %s %s' % (os.path.join(BASE_DIR,'scripts/newcustom/build_newbase.sh'),pro_name,tag)
        elif pro_type == '3':
            pro_name='%s-ats' % pro_name
            cmd='%s %s %s' % (os.path.join(BASE_DIR,'scripts/newcustom/build_newats.sh'),pro_name,tag)
        elif pro_type == '4':
            cmd='%s %s %s %s %s' % (os.path.join(BASE_DIR,'scripts/newcustom/build_newnode.sh'),pro_name,tag,branch,branch)
            pro_name='%s-node' % pro_name
        elif pro_type == '5':
            cmd='%s %s %s' % (os.path.join(BASE_DIR,'scripts/newcustom/build_newemployee.sh'),pro_name,tag)
            pro_name='%s-employee' % pro_name
        logger.info(cmd)
        if pro_type in ('4','5'):
            dockerimg='hub.ifchange.com/tobcustom/%s:%s' % (pro_name,tag)
        else:
            dockerimg='docker.ifchange.com/projects/%s:%s' % (pro_name,tag)
        logger.info(dockerimg+str(type(pro_type)))
        logger.info("start build %s......" % pro_name)
        try:
            (stat,res)=subprocess.getstatusoutput(cmd)
            logger.info('%s' % res)
            if not stat:
                CustomPro.objects.filter(pro_sign=tsign).update(build_stat=1,build_at=cur_time,dockerimg=dockerimg,deploy_stat=0)
                db=BuildHistory(build_sign=tsign,build_tag=tag,build_at=cur_time)
                db.save()
                err=[0,'构建成功']
                logger.info('构建成功'+str(res))
            else:
                CustomPro.objects.filter(pro_sign=tsign).update(build_stat=2,build_at=cur_time,deploy_stat=0)
                err=[1,'构建失败']
                logger.error('构建失败！！！'+res+'\t'+cmd)
        except Exception as e:
            print (str(e))
            CustomPro.objects.filter(pro_sign=tsign).update(build_stat=2,build_at=cur_time,deploy_stat=0)
            err=[1,str(e)]
            logger.error(str(e))
        stats=CustomPro.objects.filter(pro_sign=tsign).values()[0]['build_stat']
        msg={'stat':stats,'err':err}
    else:
        msg={'stat':1,'err':'不支持的方式'}
        logger.error('不支持的方式')
    print (msg['err'][1])
    logger.info(str(msg))
    logger.info("build %s end" % (pro_name))
    return HttpResponse(json.dumps(msg),content_type='application/json')


def asynccustom(request):
    if request.method == 'POST':
        logger.info('%s  Start sync docker .....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        datas = request.POST
        tag_env = datas['genv'].strip()
        branch=datas['codebranch'].strip()
        tagid=datas['tagsign']
        protype=datas['protype']
        proname=datas['proname']
        if protype == '2':
            if proname in ['talentrecommend']:
                sfile=os.path.join(BASE_DIR,'scripts/democustom/deploy_be.sh')
                dfile='/opt/wwwroot/deploy/democustom/deploy_be.sh'
            else:
                proname='tob_custom_base'
                sfile=os.path.join(BASE_DIR,'scripts/newcustom/deploy2.sh')
                dfile='/opt/wwwroot/deploy/tobcustom/deploy2.sh'
        elif protype == '3':
            sfile=os.path.join(BASE_DIR,'scripts/newcustom/deploy_newats.sh')
            dfile='/opt/wwwroot/deploy/tobcustom/deploy_newats.sh'
        if protype == '4':
            pproname=proname+'-node'
            port=promaps[pproname]
            sfile=os.path.join(BASE_DIR,'scripts/newcustom/deploy_newnode.sh')
            dfile='/opt/wwwroot/deploy/tobcustom/deploy_newnode.sh'
        elif protype == '5':
            pproname=proname+'-employee'
            port=promaps[pproname]
            sfile=os.path.join(BASE_DIR,'scripts/newcustom/deploy_newemployee.sh')
            dfile='/opt/wwwroot/deploy/tobcustom/deploy_newemployee.sh'
        else:
            port=promaps[proname]
        ##获取当前配置
        db = CustomPro.objects.filter(pro_sign=tagid,build_stat=1,is_delete=0)
        if not db.values():
            datas = {}
            msg={'stat':'0','info':'Not found'}
            logger.error('没有找到相应配置')
        else:
            sect=db.values().values()[0]
            if proname in ['iflytek','jinke','customize','gcampus','visionox','webank','ka-demo','tob_custom_base']:
                groups='custom'
            else:
                groups='newcustom'
            hosts=groups+'_'+tag_env
            tag=sect['dockerimg']
            logger.info("start deploy %s to %s(%s)" % (proname,tag_env,hosts))
            res=customDeploy(proname,hosts,tag,sfile,dfile,tag_env,port)
            if not res['sync']:
                errCode=1
                info=u'同步脚本失败'
                logger.error('同步脚本失败')
            elif not res['deploy']:
                errCode=1
                info=u'部署docker失败'
                logger.error('部署docker失败')
            else:
                errCode=0
                info=u'部署成功'
                logger.info('部署成功')
    else:
        errCode=1
        info=u'不支持的请求方式'
        logger.error('不支持的请求方式')
    if tag_env == 'test' or tag_env == 'testing2':
        deploy_ok=1
        deploy_err=3
    else:
        deploy_ok=2
        deploy_err=4
    if errCode:
        CustomPro.objects.filter(pro_sign=tagid).update(deploy_stat=deploy_err)
    else:
        CustomPro.objects.filter(pro_sign=tagid).update(deploy_stat=deploy_ok)
    results={'stat':errCode,'msg':info}
    print (results)
    logger.info('%s  End sync %s to %s(%s)' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),proname,tag_env,hosts))
    return HttpResponse(json.dumps(results),content_type='application/json')


def asynclocal(request):
    if request.method == 'POST':
        logger.info('%s  Start sync docker .....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
        datas = request.POST
        branch=datas['codebranch'].strip()
        tagid=datas['tagsign']
        proname=datas['proname']
        svrname=datas['svrname']
        ##获取当前配置
        errCode=0
        ctime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        db = NewLocalPro.objects.filter(pro_sign=tagid,is_delete=0)
        if not db.values():
            datas = {}
            info='Not found'
            logger.error('没有找到相应配置')
        else:
            sect=db.values().values()[0]
            logger.info("start deploy %s of %s" % (svrname,proname))
            deploycmd='sh /opt/localize/build/deployWeb.sh %s %s %s' % (proname,svrname,branch)
            res=subprocess.getstatusoutput(deploycmd)
            logger.info(str(res))
            if  res[0] == 102:
                errCode=2
                info=u'构建失败'
                logger.error('构建失败')
                NewLocalPro.objects.filter(pro_sign=tagid).update(build_stat=errCode,published_at=ctime)
            elif res[0] == 202:
                errCode=2
                info=u'部署失败'
                logger.error('部署失败')
                NewLocalPro.objects.filter(pro_sign=tagid).update(build_stat=1,deploy_stat=errCode,published_at=ctime)
            elif res[0] == 0:
                sucCode=1
                info=u'部署成功'
                logger.info('部署成功')
                NewLocalPro.objects.filter(pro_sign=tagid).update(build_stat=sucCode,deploy_stat=sucCode,published_at=ctime)
            else:
                errCode=2
                info=u'部署失败'
                logger.info('部署失败')
                NewLocalPro.objects.filter(pro_sign=tagid).update(build_stat=errCode,deploy_stat=errCode,published_at=ctime)
    results={'stat':errCode,'msg':info}
    logger.info(str(results))
    logger.info('%s  End sync %s to %s' % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),svrname,proname))
    return HttpResponse(json.dumps(results),content_type='application/json')


def syncconf(request):
    results={}
    if request.method == 'POST':
        datas=request.POST
        sfile=datas['src']
        dfile=datas['dst']
        groupname='cfg_'+datas['env']
        cmd='ansible %s -m file -a "path=%s state=directory recurse=yes"' % (groupname,os.path.dirname(dfile))
        (stat,res)=subprocess.getstatusoutput(cmd)
        if stat:
            errCode=1
            err=u'创建目录失败'
            stats=1
            logger.error('%s 创建目录 %s 失败' % (groupname,os.path.dirname(dfile)))
        else:
            ##sync cfg
            cmd='ansible %s -m copy -a "src=%s dest=%s owner=pubuser group=pubuser mode=0644"' % (groupname,sfile,dfile)
            (stat,res)=subprocess.getstatusoutput(cmd)
            logger.error(cmd+'\t'+res)
            if not stat and not 'FAILED' in res:
                errCode=0
                err=u'同步成功'
                stats=0
                logger.info('同步cfg到%s成功' % groupname)
            else:
                errCode=1
                err=u'同步失败'
                stats=1
                logger.error('同步cfg到%s失败' % groupname)
    msg={'stat':stats,'err':[errCode,err]}
    #print msg
    return HttpResponse(json.dumps(msg),content_type='application/json')

def delDocConf(request):
    if request.method == 'POST':
        sign=request.POST['sign']
        try:
            Docker.objects.filter(pro_sign=sign).update(is_delete=1)
            msg={'stat':1}
        except Exception as e:
            msg={'stat':0}
            logger.error('删除失败'+str(e))
    return HttpResponse(json.dumps(msg),content_type='application/json')
