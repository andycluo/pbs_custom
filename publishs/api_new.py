#coding:utf8
from models import *
from public import gitModule, sshSync
from django.shortcuts import HttpResponse
import time,os
import json

def aaa(request):
     print 'ss'
     return HttpResponse(json.dumps({"stat":"0", "info":"没有需要同步的tag"}))

def asynctag(request):
    username = request.session.get('username')
    if request.method == 'POST':
	print '%s  Start sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        datas = request.POST
        print datas
	print 'aaaaaaa'
	funcname=datas['opfunc'].strip()
	if funcname == 'deploy':
            branch=datas['tagbranch'].strip()
            stat=datas['stat']
	tagid=datas['tagid']
        tag_env = datas['genv'].strip()
        if tag_env == 'test':
            host = '211.148.28.19'
            port = 68
            user = 'icpublish'
            # host='192.168.1.112'
            # port=22
            # user='icpublish'
            sstat = 1
        else:
            host = '211.148.28.7'
            port = 22118
            user = 'icpublish'
            sstat = 2
	#同步代码
        syncstat = 0
        if stat:
            syncstat = 1
        ##获取当前配置
        if syncstat:
            db = Tagconf.objects.filter(tag_env=tag_env, tag_branch=branch,id=tagid)
	    print db.values()
            if not db.values():
                datas = {}
		msg={'stat':'0','info':'Not found'}
            else:
                for sect in db.values():
                    tagurl = sect['tag_url']
                    branch = sect['tag_branch']
                    codeParDir = '/opt/deploy/code/' + tagurl.split(':')[1].split('.')[0].split('/')[0]
                    codeDir = tagurl.split(':')[1].split('.')[0]
                    codepath = '/opt/deploy/code/' + codeDir
                    cur_date = time.strftime('%Y-%m-%d', time.localtime())
                    fulltar = '/opt/zipdir/fe_full_%s.tar.gz' % cur_date
                    bezip = '/opt/zipdir/fe_incr_%s.zip' % cur_date
                    git = gitModule(tagurl)
                    if not os.path.exists(codeParDir):
                        os.system('mkdir %s -p' % codeParDir)
                    if not os.path.exists(codepath):
                        git.clone(codepath)
                        msg = {"stat":"1", "info":''}
			print msg
                    elif 'master' in branch:
                        dstpath = '/opt/zipdir/fe_full_%s.tar.gz' % cur_date
                        print dstpath
                        delfiles = ['']
                        ret = git.checkout('master', codepath, fulltar)
                        if ret:
                            # res=sshSync(host,port,user,fulltar,dstpath,'/usr/bin/python /home/icpublish/deploy.py %s %s "%s" %s' % (codeDir,fulltar,delfiles,cur_date))
                            res = sshSync(host, port, user, fulltar, dstpath,
                                          '/usr/bin/python /opt/userhome/icpublish/deploy.py %s %s "%s" %s' % (
                                          codeDir, fulltar, delfiles, cur_date))
                            print res
                            if 'finish' in res and not 'failed' in res:
                                if tag_env == 'online':
                                    Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat, tag_env='online')
				else:
                    		    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                    Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,published_at=cur_time)
				msg={"stat":"1","info":"同步成功"}
                            else:
                                msg={"stat":"0","info":"同步失败"}
                        else:
                            msg = {"stat":"0", "info":"获取全量文件失败"}
			#return msg
			print msg
                    else:
                        try:
                            datas = Tagconf.objects.filter(tag_env='online', status=2).order_by(
                                '-created_at').values()
                            print datas[0]['tag_branch']
                            if datas:
                                lasttag = datas[0]['tag_branch']
                            else:
                                lasttag = 0
                        except Exception as e:
                            print str(e)
			print lasttag
                        if not lasttag:
                            dstpath = '/opt/zipdir/fe_full_%s.tar.gz' % cur_date
                            rets = git.checkout(branch, codepath, fulltar)
                        else:
                            dstpath = '/opt/zipdir/fe_incr_%s.zip' % cur_date
                            rets = git.diff(branch,lasttag, bezip, codepath)
                        print rets
                        if rets:
                            if lasttag:
                                incrfile = rets[0]
                                delfiles = rets[1]
                                if incrfile:
                                    # res=sshSync(host, port,user, incrfile, dstpath, '/usr/bin/python /home/icpublish/deploy.py %s %s "%s" %s' % (codeDir,incrfile,delfiles,cur_date))
                                    res = sshSync(host, port, user, incrfile, dstpath,
                                                  '/usr/bin/python /opt/userhome/icpublish/deploy.py %s %s "%s" %s' % (
                                                  codeDir, incrfile, delfiles, cur_date))
                                    if 'finish' in res and not 'failed' in res:
                                        msg = {"stat":"1", "info":"同步完成"}
                                        if tag_env == 'online':
                                            Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,
                                                                                             tag_env='online')
					else:
                    			    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                                    	    Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,published_at=cur_time)
                                    else:
                                        msg = {"stat":"0", "info":"同步失败"}
                            else:
                                delfiles = ['']
                                res = sshSync(host, port, user, fulltar, dstpath,
                                              '/usr/bin/python /opt/userhome/icpublish/deploy.py %s %s "%s" %s' % (
                                              codeDir, fulltar, delfiles, cur_date))
                                print res
                                if 'finish' in res and not 'failed' in res:
                                    msg = {"stat":"1", "info":"同步完成"}
                                    if tag_env == 'online':
                                        Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,
                                                                                         tag_env='online')
				    else:
                    			cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
					Tagconf.objects.filter(tag_branch=branch,id=tagid).update(status=sstat,published_at=cur_time)
                                else:
                                    msg = {"stat":"0", "info":"同步失败"}
                        else:
                            msg = {"stat":"0", "info":"获取增量文件失败"}
			print msg
        else:
            msg = {"stat":"0", "info":"没有需要同步的tag"}
	print '%s  End sync.....' % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        return HttpResponse(json.dumps(msg),content_type='application/json')
