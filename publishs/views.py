# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render_to_response, HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from publishs.models import *
from django.utils import timezone
from publishs.public import gitModule, sshSync, diffConf
#from public import gitModule, sshSync, diffConf
from collections import OrderedDict
import os, time, json
import logging
import hashlib

logger = logging.getLogger('django')
BASEDIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create your views here.

##用户登录
def login(request):
    if request.method == 'POST':
        data = request.POST
        name = data['user']
        pwd = data['pwd']
        try:
            realData = User.objects.get(name=name)
            if check_password(pwd, realData.pwd):
                request.session['is_login'] = True
                request.session['username'] = name
                return HttpResponseRedirect('/publish/index/')
            else:
                error = {'msg': '账号或密码错误'}
                return HttpResponseRedirect('/publish/', context=error)
        except Exception as e:
            return HttpResponseRedirect('/publish/')
    else:
        return render_to_response('login.html')


##首页
def index(request):
    islogin = request.session.get('is_login', False)
    username = request.session.get('username')
    if islogin:
        return render_to_response('index.html', {'username': username})
    else:
        return HttpResponseRedirect('/publish/')


##退出
def logout(request):
    del request.session
    return HttpResponseRedirect('/publish/')


##添加gm配置
def addgm(request):
    genv = 'default'
    username = request.session.get('username')
    if request.method == 'POST':
        data = request.POST
        work_name = data['wname']
        gm_server = data['gserver']
        gm_port = data['gport']
        gm_env = data['genv']
        try:
            if Gmconf.objects.get(work_name=work_name, gm_env=gm_env):
                msg = '%s of %s already exist' % (work_name, gm_env)
                request.session['err'] = msg
                return HttpResponseRedirect('/publish/addgm/')
        except:
            try:
                db1 = Gmconf(work_name=work_name, gm_server=gm_server, gm_port=gm_port, gm_env=gm_env)
                db1.save()
                return HttpResponseRedirect('/publish/addgm/')
            except Exception as e:
                print (str(e))
                msg = 'Add %s of %s failed' % (work_name, gm_env)
                request.session['err'] = msg
                return HttpResponseRedirect('/publish/addgm/')
    else:
        if request.GET.has_key('genv') and request.GET['genv'] != 'default':
            genv = request.GET['genv']
            datas = Gmconf.objects.filter(gm_env=genv, status=1).values()
        else:
            datas = Gmconf.objects.filter(status=1).values()
    if request.session.has_key('err'):
        err_msg = request.session['err']
        del request.session['err']
    else:
        err_msg = False
    return render_to_response('addgm.html', {'username': username, 'datas': datas, 'err_msg': err_msg, 'selenv': genv})


def syncgm(request):
    username = request.session.get('username')
    if request.GET.has_key('genv') and request.GET['genv'] != 'default':
        genv = request.GET['genv']
        datas = Gmconf.objects.filter(status=0, gm_env=genv).values()
    else:
        datas = Gmconf.objects.filter(status=0).values()
        genv = 'default'
    return render_to_response('syncgm.html', {'username': username, 'datas': datas, 'selenv': genv})


def syncgming(request):
    username = request.session.get('username')
    if request.method == 'POST':
        datas = request.POST
        cenv = datas['genv'].strip()
        gmconf = '/opt/wwwroot/conf/gm_%s.conf' % cenv
        ##获取当前配置
        f = open(gmconf, 'r')
        cont = eval(f.read())
        for work in datas.keys():
            if work == 'genv':
                continue
            data = datas.getlist(work)
            if data[0] == '0':
                continue
            db = Gmconf.objects.filter(gm_env=cenv, id=int(data[1].strip()))
            for sect in db.values():
                gm_server = sect['gm_server']
                gm_port = sect['gm_port']
            ##添加新配置
            cont[work] = {'host': ["%s:%s" % (gm_server, gm_port)]}
            Gmconf.objects.filter(id=int(data[1].strip())).update(status=1, published_at=timezone.now())
        f = open(gmconf, 'w')
        f.write(str(cont).encode('utf8'))
        f.close()
    return HttpResponseRedirect('/publish/addgm/')


##添加tag配置
def addtag(request):
    tag_env = 'default'
    username = request.session.get('username')
    cur_date = time.strftime('%Y-%m-%d', time.localtime())
    if request.method == 'POST':
        data = request.POST
        tag_url = data['tagurl'].strip()
        branch = data['branch'].strip()
        tag_env = data['genv'].strip()
        pro_name = tag_url.split(':')[1].split('.')[0].replace('/','_')
        logger.info('%s %s %s' % (tag_url,branch,tag_env))
        ##获取branch
        if branch:
            if branch == '0':
                branch = 'master'
            try:
                if Tagconf.objects.get(tag_url=tag_url, tag_env=tag_env, tag_branch=branch,pro_name=pro_name):
                    msg = '%s of %s on %s already exist' % (branch, tag_url, tag_env)
                    request.session['err'] = msg
                    return HttpResponseRedirect('/publish/addtag/')
            except:
                try:
                    db1 = Tagconf(tag_url=tag_url, tag_branch=branch, tag_env=tag_env,pro_name=pro_name)
                    db1.save()
                    return HttpResponseRedirect('/publish/addtag/')
                except Exception as e:
                    print (str(e))
                    msg = 'Add %s of %s on %s failed' % (branch, tag_url, tag_env)
                    request.session['err'] = msg
                    return HttpResponseRedirect('/publish/addtag/')
        else:
            request.session['err'] = '版本未指定，添加失败'
            return HttpResponseRedirect('/publish/addtag/')
    else:
        if request.GET.has_key('genv') and request.GET['genv'] != 'default':
            datas = Tagconf.objects.filter(tag_env=tag_env, status=0).values()
        else:
            datas = Tagconf.objects.filter(status=0).order_by('-created_at').values()
    if request.session.has_key('err'):
        err_msg = [1, request.session['err']]
        del request.session['err']
    else:
        err_msg = [0, '']
    return render_to_response('addtag.html',
                              {'username': username, 'datas': datas, 'err_msg': err_msg, 'selenv': tag_env})


def synctag(request):
    username = request.session.get('username')
    if  request.method == 'GET':
        ONE_PAGE_DATA = 10
        try:
            curPage = int(request.GET.get('curPage','1'))
            pageType = str(request.GET.get('pageType',''))
        except ValueError:
            curPage = 1
            pageType = ''
        if pageType == 'pageDown':
           curPage += 1
        elif pageType == 'pageUp':
           curPage -= 1
        startPos = (curPage - 1) * ONE_PAGE_DATA
        endPos = startPos + ONE_PAGE_DATA

        if request.GET.items():
            if 'id' in request.GET.items()[0] and 'tenv' in request.GET.items()[1]:
                tid = request.GET['id']
                tag_env = request.GET['tenv']
                tmp=Tagconf.objects.filter(id=tid).values()
                for td in tmp:
                    tag_url=td['tag_url']
                    tag_branch=td['tag_branch']
                    pub_tag=td['last_published_tag']
                if tag_env == 'online':
                    Tagconf.objects.filter(tag_url=tag_url,tag_env='testing2',tag_branch=tag_branch).update(status=1, tag_env='online')
                    return HttpResponseRedirect('/publish/synctag/?tenv=online')
                elif tag_env == 'testing2':
                    Tagconf.objects.filter(id=tid).update(status=1, tag_env='testing2',t_last_published_tag=pub_tag)
                    return HttpResponseRedirect('/publish/synctag/?tenv=testing2')
                elif tag_env == 'testing3':
                    Tagconf.objects.filter(id=tid).update(status=0, tag_env='testing3',t3_last_published_tag=pub_tag)
                    return HttpResponseRedirect('/publish/synctag/?tenv=testing3')
                else:
                    Tagconf.objects.filter(id=tid).update(status=1, tag_env='testing2',t_last_published_tag=pub_tag)
                    return HttpResponseRedirect('/publish/synctag/?tenv=testing2')
            elif 'tenv' in request.GET.items()[0]:
                tag_env = request.GET['tenv'].strip()
                if tag_env == 'default':
                    datas = Tagconf.objects.raw('select * from publishs_tagconf group by tag_url,tag_env,status,tag_branch,pro_name order by id desc')
                elif tag_env == 'testing2':
                    ###datas = Tagconf.objects.values('tag_env','tag_branch').order_by('-published_at')
                    datas = Tagconf.objects.raw('select * from (select * from publishs_tagconf where tag_env="testing2" order by t_published_at desc) as t  group by t.tag_url,t.tag_env,t.tag_branch order by t.t_published_at desc')
                elif tag_env == 'testing3':
                    datas = Tagconf.objects.raw('select * from (select * from publishs_tagconf where tag_env="testing3" order by t3_published_at desc) as t  group by t.tag_url,t.tag_env,t.tag_branch order by t.t3_published_at desc')
                else:
                    ###datas = Tagconf.objects.exclude(status=0).values()
                    datas = Tagconf.objects.raw(
                        'select * from (select * from publishs_tagconf where tag_env="online" order by published_at desc) as o  group by o.tag_url,o.tag_env,o.tag_branch order by o.published_at desc')
            else:
                tag_env = 'default'
                datas = Tagconf.objects.raw('select * from (select * from publishs_tagconf order by published_at desc) as d group by d.tag_url,d.tag_env,d.tag_branch order by d.id desc')
        err_msg = [0, '']
    else:
        err_msg = [1,'request method not support']
        datas = Tagconf.objects.all().values()
    counts = len(list(datas))
    datas = list(datas)[startPos:endPos]
    pages = counts/ONE_PAGE_DATA
    remainCounts = counts%ONE_PAGE_DATA
    if remainCounts > 0:
        pages += 1

    return render_to_response('synctag.html',
                          {'username': username, 'datas': datas, 'err_msg': err_msg, 'selenv': tag_env,'totalPage':pages,'curPage':curPage})
def syncfe(request):
    username = request.session.get('username')
    if  request.method == 'GET':
        ONE_PAGE_DATA = 6
        try:
            curPage = int(request.GET.get('curPage','1'))
            pageType = str(request.GET.get('pageType',''))
        except ValueError:
            curPage = 1
            pageType = ''
        if pageType == 'pageDown':
           curPage += 1
        elif pageType == 'pageUp':
           curPage -= 1
        startPos = (curPage - 1) * ONE_PAGE_DATA
        endPos = startPos + ONE_PAGE_DATA
        if request.GET.items():
            if 'id' in request.GET.items()[0] and 'tenv' in request.GET.items()[1]:
                tid = request.GET['id']
                tag_env = request.GET['tenv']
                tmp=CustomPro.objects.filter(id=tid).values()
                for td in tmp:
                    tag_url=td['tag_url']
                    tag_branch=td['code_branch']
                if tag_env == 'pro':
                    CustomPro.objects.filter(id=tid).update(deploy_stat=1, tag_env=2)
                    return HttpResponseRedirect('/publish/deployfe/?tenv=pro')
                elif tag_env == 'test':
                    CustomPro.objects.filter(id=tid).update(deploy_stat=1, tag_env=1)
                    return HttpResponseRedirect('/publish/deployfe/?tenv=test')
                else:
                    CustomPro.objects.filter(id=tid).update(deploy_stat=1, tag_env=1)
                    return HttpResponseRedirect('/publish/deployfe/?tenv=test')
            elif len(request.GET.items()) == 3 and 'tenv' in request.GET.items()[2]:
                envdict={'test':1,'pro':2}
                tag_env=request.GET.items()[2][1]
                try:
                    if tag_env != 'default':
                        tenv=envdict[tag_env]
                        #datas = CustomPro.objects.filter(is_delete=0,tag_env=tenv).order_by('-build_at')
                        datas = CustomPro.objects.filter(is_delete=0,tag_env=tenv).order_by('-published_at')
                    else:
                        datas = CustomPro.objects.filter(is_delete=0).order_by('-published_at')
                    err_msg = [0,'']
                    #logger.info(str([key,data[key] for key in data  for data in datas])+str(curPage))
                except Exception as e:
                    err_msg = [1,'Databse connect failed\n'+str(e)]
                    logger.error('Databse connect failed. '+str(e))
            elif 'tenv' in request.GET.keys():
                tag_env = request.GET['tenv'].strip()
                print (tag_env)
                if tag_env == 'default':
                    #datas = CustomPro.objects.raw('select * from publishs_custompro  group by tag_url,tag_env,deploy_stat,code_branch,pro_name order by id desc')
                    datas = CustomPro.objects.raw('select * from publishs_custompro where pro_type<>4  group by tag_url,tag_env,deploy_stat,code_branch,pro_name order by published_at desc')
                elif tag_env == 'test':
                    #datas = CustomPro.objects.raw('select * from (select * from publishs_custompro where tag_env=1 order by published_at desc) as t  group by t.pro_name,t.tag_url,t.tag_env,t.code_branch,t.pro_type order by t.build_at desc')
                    datas = CustomPro.objects.raw('select * from (select * from publishs_custompro where tag_env=1 and pro_type<>4 order by published_at desc) as t  group by t.pro_name,t.tag_url,t.tag_env,t.code_branch,t.pro_type order by t.published_at desc')
                else:
                    #datas = CustomPro.objects.raw(
                    #    'select * from (select * from publishs_custompro where tag_env=2  order by published_at desc) as o  group by o.pro_name,o.tag_url,o.tag_env,o.code_branch,o.pro_type order by o.build_at desc')
                    datas = CustomPro.objects.raw(
                        'select * from (select * from publishs_custompro where tag_env=2 and pro_type<>4  order by published_at desc) as o  group by o.pro_name,o.tag_url,o.tag_env,o.code_branch,o.pro_type order by o.published_at desc')
            else:
                tag_env = 'default'
                #datas = CustomPro.objects.raw('select * from (select * from publishs_custompro  order by published_at desc) as d group by d.pro_name,d.tag_url,d.tag_env,d.code_branch,d.pro_type order by d.id desc')
                datas = CustomPro.objects.raw('select * from (select * from publishs_custompro where pro_type<>4  order by published_at desc) as d group by d.pro_name,d.tag_url,d.tag_env,d.code_branch,d.pro_type order by d.published_at desc')
        else:
            tag_env = 'default'
            #datas = CustomPro.objects.raw('select * from (select * from publishs_custompro  order by published_at desc) as d group by d.pro_name,d.tag_url,d.tag_env,d.code_branch order by d.id desc')
            datas = CustomPro.objects.raw('select * from (select * from publishs_custompro  order by published_at desc) as d group by d.pro_name,d.tag_url,d.tag_env,d.code_branch order by d.published_at desc')
        err_msg = [0, '']
    else:
        err_msg = [1,'request method not support']
        try:
            datas = CustomPro.objects.all().values()
        except Exception as e:
            print (str(e))
    counts = len(list(datas))
    datas = list(datas)[startPos:endPos]
    pages = counts/ONE_PAGE_DATA
    remainCounts = counts%ONE_PAGE_DATA
    if remainCounts > 0:
        pages += 1
    return render_to_response('syncfe.html',
                          {'username': username, 'datas': datas, 'err_msg': err_msg, 'selenv': tag_env,'totalPage':pages,'curPage':curPage})

def rollback(request):
    username = request.session.get('username')
    if request.method == 'GET':
        if request.GET.items():
            if len(request.GET.items()) == 3 and 'tenv' in request.GET.items()[2] and 'tag' in request.GET.items()[1] and 'pro'in request.GET.items()[0]:
                tag_env = request.GET['tenv'].strip()
                tagname = request.GET['tag'].strip()
                proname = request.GET['pro'].strip()
                try:

                    #datas = Tagconf.objects.filter(tag_env=tag_env,tag_branch=tagname,pro_name=proname).order_by('-last_published_tag').values()[:10]
                    if tag_env == 'test':
                        datas = Tagconf.objects.raw(
                            'select * from publishs_tagconf where tag_env="%s" and tag_branch="%s" and pro_name="%s" and t_last_published_tag <> "" group by t_last_published_tag  order by t_last_published_tag desc limit 6' % (tag_env,tagname,proname))
                    else:
                        datas = Tagconf.objects.raw(
                            'select * from publishs_tagconf where tag_env="%s" and tag_branch="%s" and pro_name="%s" and last_published_tag <> "" group by last_published_tag order by last_published_tag desc limit 6' % (tag_env,tagname,proname))
                    err_msg = [0,'']
                except Exception as e:
                    err_msg = ['1','Databse connect failed\n'+str(e)]
            else:
                tag_env = request.GET['tenv'].strip()
                try:
                    if tag_env == 'default':
                        #datas = Tagconf.objects.order_by('-last_published_tag').values()[:10]
                        datas = Tagconf.objects.raw(
                            'select * from publishs_tagconf order by id desc limit 6')
                    elif tag_env == 'test':
                        #datas = Tagconf.objects.filter(tag_env=tag_env).order_by('-last_published_tag').values()[:10]
                        datas = Tagconf.objects.raw(
                            'select * from publishs_tagconf where tag_env="%s" group by tag_url,t_last_published_tag  order by t_last_published_tag desc limit 6' % tag_env)
                    else:
                       datas = Tagconf.objects.raw(
                            'select * from publishs_tagconf where tag_env="%s" group by tag_url,last_published_tag  order by last_published_tag desc limit 6' % tag_env)
                    err_msg = [0,'']
                except Exception as e:
                    err_msg = ['1','Databse connect failed\n'+str(e)]
        else:
            err_msg = ['1','不支持的请求']
    return render_to_response('rollbacktag.html',
                          {'username': username, 'datas': datas, 'err_msg': err_msg, 'selenv': tag_env})

def dockercfg(request):
    username = request.session.get('username')
    if request.method == 'POST':
        newcfg=request.POST['cfg'].encode('utf8')
        ##newcfg=request.POST['cfg'].replace('\r\n','').replace(',}','}')
        newdata=json.loads(newcfg.replace(',\r\n}','\r\n}'),encoding='utf-8')
        menv=request.POST['env']
        #olddata=Dockerconf.objects.filter(denv=menv).values()
        cfg=os.path.join(BASEDIR,'conf/%s/docker.conf' % menv)
        cont=open(cfg,'r').read().strip()
        if cont:
            olddata=json.loads(cont)
        else:
            olddata={}
        res=diffConf(newdata,olddata)
        #print json.loads(res)
        errCode=0
        if res['add'] or res['del'] or res['mod']:
            if res['add']:
                for pro in res['add'].keys():
                    try:
                        db=Dockerconf(denv=menv,pro_name=pro,deploy_list=json.dumps(res['add'][pro]['deplist']),hosts=json.dumps(res['add'][pro]['host']))
                        db.save()
                    except Exception as e:
                        logger.error('add cfg err. '+str(e))
                        errCode=1
                        err='add config err'
                errCode=0
                err=''
            elif res['mod']:
                for pro in res['mod'].keys():
                    try:
                        Dockerconf.objects.filter(denv=menv,pro_name=pro).update(deploy_list=json.dumps(res['mod'][pro]['deplist']),hosts=json.dumps(res['mod'][pro]['host']))
                    except Exception as e:
                        logger.error('modify cfg err. '+str(e))
                        errCode=1
                        err='modify config err'
                errCode=0
                err=''
            elif res['del']:
                for pro in res['del'].keys():
                    try:
                       p=Dockerconf.objects.get(denv=menv,pro_name=pro)
                       p.delete()
                    except Exception as e:
                        logger.error('delete cfg err. '+str(e))
                        errCode=1
                        err='delete config err'
                errCode=0
                err=''
            if not errCode:
                json.dump(newdata,open(cfg,'w'))
        else:
            errCode=0
            err='配置文件无需更新'
        datas=Dockerconf.objects.filter(denv=menv).values()
    else:
        res={}
        menv=request.GET['env']
        if menv in ['test','pro']:
            try:
                datas=Dockerconf.objects.filter(denv=menv).values()
                errCode=0
                err=''
                logger.warn('get cfg from db failed.')
            except:
                cfg=os.path.join(BASEDIR,'conf/%s/docker.conf' % menv)
                if os.path.exists(cfg):
                    content=json.loads(open(cfg).read())
                    errCode=0
                    err=''
                    logger.warn('get cfg from file failed.')
                else:
                    err='友情提示：获取配置文件失败'
                    errCode=1
                    logger.error('友情提示：获取配置文件失败')
        else:
            datas=''
            err='友情提示：请选择环境'
            errCode=1
            logger.error('环境未选择')
    err_msg=[errCode,err]
    return render_to_response('dockercfg.html',
                          {'username': username, 'datas': datas, 'err_msg': err_msg,'env':menv,'res':res})

def buildimg(request):
    username = request.session.get('username')
    logger.info(username)
    if request.method == 'GET':
       ONE_PAGE_DATA = 10 
       try:
           curPage = int(request.GET.get('curPage','1'))
           pageType = str(request.GET.get('pageType',''))
       except ValueError:
           curPage = 1 
           pageType = ''
       if pageType == 'pageDown':
          curPage += 1
       elif pageType == 'pageUp':
          curPage -= 1
       startPos = (curPage - 1) * ONE_PAGE_DATA
       endPos = startPos + ONE_PAGE_DATA
       try:
           #datas = Docker.objects.raw('select id,pro_name,code_branch as fe_branch,code_branch as be_branch,pro_type,created_at,build_at,published_at,pro_sign from publishs_docker where is_delete=0  group by pro_name,tag_env,created_at order by created_at desc')
           tdatas = Docker.objects.raw('select * from pbs_test.docker_page order by build_at desc')
           counts = len(list(tdatas))
           datas = list(tdatas)[startPos:endPos]
           pages = counts/ONE_PAGE_DATA
           remainCounts = counts%ONE_PAGE_DATA
           if remainCounts > 0:
               pages += 1
           err_msg = [0,'']
           #logger.info(str([key,data[key] for key in data  for data in datas])+str(curPage))
       except Exception as e:
           err_msg = [1,'Databse connect failed\n'+str(e)]
           logger.error('Databse connect failed. '+str(e))
    else:
       err_msg = [1,'不支持的请求']
       logger.error('不支持的请求')
    return render_to_response('builddocker.html',
                          {'username': username, 'datas': datas,'totalPage':pages,'curPage':curPage, 'err_msg': err_msg})
def addtag2(request):
    tag_env = 'default'
    username = request.session.get('username')
    cur_date = time.strftime('%Y-%m-%d', time.localtime())
    if request.method == 'POST':
        data = request.POST
        tag_url = data['tagurl'].strip()
        branch = data['branch'].strip()
        tagenv = data['genv'].strip()
        if tagenv == 'pro':
            tag_env=2
        else:
            tag_env=1
        pro_name = tag_url.split(':')[1].split('.')[0].split('/')[1]
        pro_sign = hashlib.md5(pro_name+time.strftime('%Y%m%d%H%M%S', time.localtime())).hexdigest()
        ##获取branch
        if branch:
            if branch == '0':
                branch = 'master'
            try:
                if Docker.objects.filter(is_delete=0).get(tag_url=tag_url, tag_env=tag_env, code_branch=branch,pro_name=pro_name):
                    msg = '%s of %s on %s already exist' % (branch, tag_url, tagenv)
                    request.session['err'] = msg
                    logger.info('%s of %s on %s already exist' % (branch, tag_url, tagenv))
                    #return HttpResponseRedirect('/publish/addtag2/')
                    return HttpResponseRedirect('/publish/addmultitag/')
            except:
                try:
                    db1 = Docker(tag_url=tag_url, code_branch=branch, tag_env=tag_env,pro_name=pro_name,pro_sign=pro_sign)
                    db1.save()
                    msg='Add %s successfully' % tag_url
                    return HttpResponseRedirect('/publish/addmultitag/')
                except Exception as e:
                    msg = 'Add %s of %s on %s failed' % (branch, tag_url, tagenv)
                    logger.error('Add %s of %s on %s failed' % (branch, tag_url, tagenv)+str(e))
                    request.session['err'] = msg
                    return HttpResponseRedirect('/publish/addmultitag/')
        else:
            request.session['err'] = '版本未指定，添加失败'
            logger.error('版本未指定，添加失败')
            return HttpResponseRedirect('/publish/addmultitag/')
    else:
        if request.GET.has_key('genv') and request.GET['genv'] != 'default':
            datas = Docker.objects.filter(tag_env=tag_env, deploy_stat=0).values()
        else:
            datas = Docker.objects.filter(deploy_stat=0).order_by('-created_at').values()
        msg=''
    if request.session.has_key('err'):
        err_msg = [1, request.session['err']]
        del request.session['err']
    else:
        err_msg = [0, msg]
    return render_to_response('addmultitag.html',
                              {'username': username, 'datas': datas, 'err_msg': err_msg})

def addapp(request):
    tag_env = 'default'
    username = request.session.get('username')
    cur_date = time.strftime('%Y-%m-%d', time.localtime())
    if request.method == 'POST':
        data = request.POST
        tag_url = data['appname'].strip()
        branch = data['branch'].strip()
        tagenv = data['genv'].strip()
        pro_type = data['protype'].strip()
        if tagenv == 'pro':
            tag_env=2
        else:
            tag_env=1
        pro_name = tag_url
        pro_sign = hashlib.md5(pro_name+time.strftime('%Y%m%d%H%M%S', time.localtime())).hexdigest()
        ##获取branch
        if branch:
            if branch == '0':
                branch = 'master'
            try:
                if Docker.objects.filter(is_delete=0).get(tag_url=tag_url, tag_env=tag_env, code_branch=branch,pro_name=pro_name):
                    msg = '%s of %s on %s already exist' % (branch, tag_url, tagenv)
                    request.session['err'] = msg
                    logger.info('%s of %s on %s already exist' % (branch, tag_url, tagenv))
                    return HttpResponseRedirect('/publish/addmultitag/')
            except:
                try:
                    db1 = Docker(tag_url=tag_url, code_branch=branch, tag_env=tag_env,pro_name=pro_name,pro_sign=pro_sign,pro_type=pro_type)
                    db1.save()
                    msg='Add %s successfully' % tag_url
                    return HttpResponseRedirect('/publish/addmultitag/')
                except Exception as e:
                    msg = 'Add %s of %s on %s failed' % (branch, tag_url, tagenv)
                    logger.error('Add %s of %s on %s failed' % (branch, tag_url, tagenv)+str(e))
                    request.session['err'] = msg
                    return HttpResponseRedirect('/publish/addmultitag/')
        else:
            request.session['err'] = '版本未指定，添加失败'
            logger.error('版本未指定，添加失败')
            return HttpResponseRedirect('/publish/addmultitag/')
    else:
        if request.GET.has_key('genv') and request.GET['genv'] != 'default':
            datas = Docker.objects.filter(tag_env=tag_env, deploy_stat=0).values()
        else:
            datas = Docker.objects.filter(deploy_stat=0).order_by('-created_at').values()
        msg=''
    if request.session.has_key('err'):
        err_msg = [1, request.session['err']]
        del request.session['err']
    else:
        err_msg = [0, msg]
    return render_to_response('addmultitag.html',
                              {'username': username, 'datas': datas, 'err_msg': err_msg})
def addcustom(request):
	tag_env = 'default'
	username = request.session.get('username')
	cur_date = time.strftime('%Y-%m-%d', time.localtime())
	if request.method == 'POST':
		data = request.POST
		tag_url = data['giturl'].strip()
		customname = data['customname'].strip()
		branch = data['branch'].strip()
		tagenv = data['genv'].strip()
		pro_type = data['protype'].strip()
		if tagenv == 'pro':
			tag_env=2
		else:
			tag_env=1
		prodict={'fe':1,'base':2,'ats':3,'node':4,'employee':5}
		pro_type=prodict[pro_type]
		pro_name = customname
		pro_sign = hashlib.md5(pro_name+time.strftime('%Y%m%d%H%M%S', time.localtime())).hexdigest()
		##获取branch
		if branch:
			try:
				if CustomPro.objects.filter(is_delete=0).get(tag_url=tag_url, tag_env=tag_env, code_branch=branch,pro_name=pro_name):
					msg = '%s of %s on %s already exist' % (branch, tag_url, tagenv)
					request.session['err'] = msg
					logger.info('%s of %s on %s already exist' % (branch, tag_url, tagenv))
					return HttpResponseRedirect('/publish/addcustom/')
			except:
				try:
					db1 = CustomPro(tag_url=tag_url, code_branch=branch, tag_env=tag_env,pro_name=pro_name,pro_sign=pro_sign,pro_type=pro_type)
					db1.save()
					msg='Add %s successfully' % tag_url
					return HttpResponseRedirect('/publish/addcustom/')
				except Exception as e:
					print (str(e))
					msg = 'Add %s of %s on %s failed' % (branch, tag_url, tagenv)
					logger.error('Add %s of %s on %s failed' % (branch, tag_url, tagenv)+str(e))
					request.session['err'] = msg
					return HttpResponseRedirect('/publish/addcustom/')
		else:
			request.session['err'] = '版本未指定，添加失败'
			logger.error('版本未指定，添加失败')
			return HttpResponseRedirect('/publish/addcustom/')
	else:
		if request.GET.has_key('genv') and request.GET['genv'] != 'default':
			datas = CustomPro.objects.filter(tag_env=tag_env, deploy_stat=0).values()
		else:
			datas = CustomPro.objects.filter(deploy_stat=0).order_by('-created_at').values()
		msg=''
	if request.session.has_key('err'):
		err_msg = [1, request.session['err']]
		del request.session['err']
	else:
		err_msg = [0, msg]
	return render_to_response('addcustom.html',
                              {'username': username, 'datas': datas, 'err_msg': err_msg})

def addlocal(request):
    svrmap={'git@192.168.1.199:web/be.git':'tob-be','git@192.168.1.199:web/fe.git':'tob-fe','git@192.168.1.199:ifchange/fe.git':'ifchange-fe','git@192.168.1.199:f2e/common.git':'common','git@192.168.1.199:f2e/public.git':'public','git@192.168.1.199:web/tob-ats.git':'tob-ats','git@192.168.1.199:web/common-employee.git':'common-employee','git@192.168.1.199:soa/ka-local-basic.git':'common-basic','git@192.168.1.199:soa/tob-resume-service.git':'tob-resume-service','git@192.168.1.199:soa/tob-es.git':'tob-es','git@192.168.1.5:haifeng.wu/grab.git':'grab','git@192.168.1.199:soa/tob-resume-pdf.git':'tob-pdf','git@192.168.1.199:soa/tob-account.git':'tob-account','git@192.168.1.199:soa/tob-data-track.git':'tob-data-track','git@192.168.1.199:web/report.git':'tob-report'}
    username = request.session.get('username')
    cur_date = time.strftime('%Y-%m-%d', time.localtime())
    msg=''
    if request.method == 'POST':
        data = request.POST
        tag_url = data['giturl'].strip()
        proname = data['proname'].strip()
        if svrmap.has_key(tag_url):
            svrname=svrmap[tag_url]
        elif tag_url.startswith('docker.ifchange.com/toc/backend/php-local-neitui'):
            svrname='toc-neitui'
        elif tag_url.startswith('docker.ifchange.com/toc/backend/php-local'):
            svrname='toc-ai'
        elif tag_url.startswith('docker.ifchange.com/toc/frontend-bole_pc') or tag_url.startswith('docker.ifchange.com/toc/f+rontend-bole-pc-'):
            svrname='neitui-bole'
        elif tag_url.startswith('docker.ifchange.com/toc/frontend-bole_mobile'):
            svrname='m-neitui-bole'
        elif tag_url.startswith('docker.ifchange.com/toc/frontend-bole-mobile'):
            svrname='m-neitui-bole'
        elif tag_url.startswith('docker.ifchange.com/toc/frontend-referral'):
            svrname='neitui-hr'
        elif tag_url.startswith('docker.ifchange.com/toc/frontend-candidate-pc'):
            svrname='neitui-candidate'
        elif tag_url.startswith('docker.ifchange.com/toc/frontend'):
            svrname='toc-node'
        elif tag_url.startswith('hub.ifchange.com/localpros/hunter'):
            svrname='hunter'
        else:
            request.session['err'] = '项目未找到，添加失败'
            logger.error('项目未找到，添加失败')
            return HttpResponseRedirect('/publish/addlocal/')
        #svrname = data['svrname'].strip()
        branch = data['branch'].strip()
        pro_sign = hashlib.md5(proname+time.strftime('%Y%m%d%H%M%S', time.localtime())).hexdigest()
##获取branch
        if branch:
            try:
                if NewLocalPro.objects.filter(is_delete=0).get(tag_url=tag_url, proname=proname,svrname=svrname, code_branch=branch):
                    msg = '%s of %s on %s already exist' % (branch, tag_url, proname)
                    request.session['err'] = msg
                    logger.info('%s of %s on %s already exist' % (branch, tag_url, proname))
                    return HttpResponseRedirect('/publish/addlocal/')
            except:
                try:
                    db1 = NewLocalPro(tag_url=tag_url, code_branch=branch,proname=proname,svrname=svrname,pro_sign=pro_sign)
                    db1.save()
                    msg='Add %s of %s on %s successfully' % (branch,tag_url,proname)
                    return HttpResponseRedirect('/publish/addlocal/')
                except Exception as e:
                    print (str(e))
                    msg = 'Add %s of %s on %s failed' % (branch, tag_url, proname)
                    logger.error('Add %s of %s on %s failed' % (branch, tag_url, proname)+str(e))
                    request.session['err'] = msg
                    return HttpResponseRedirect('/publish/addlocal/')
        else:
            request.session['err'] = '版本未指定，添加失败'
            logger.error('版本未指定，添加失败')
            return HttpResponseRedirect('/publish/addlocal/')
    else:
        datas = NewLocalPro.objects.filter(deploy_stat=0).order_by('-created_at').values()
    if request.session.has_key('err'):
        err_msg = [1, request.session['err']]
        del request.session['err']
    else:
        err_msg = [0, msg]
    return render_to_response('addlocal.html',
                              {'username': username, 'datas': datas, 'err_msg': err_msg})
def synclocal(request):
    username = request.session.get('username')
    if request.method == 'GET':
       ONE_PAGE_DATA = 10 
       try:
           curPage = int(request.GET.get('curPage','1'))
           pageType = str(request.GET.get('pageType',''))
       except ValueError:
           curPage = 1 
           pageType = ''
       if pageType == 'pageDown':
          curPage += 1
       elif pageType == 'pageUp':
          curPage -= 1
       startPos = (curPage - 1) * ONE_PAGE_DATA
       endPos = startPos + ONE_PAGE_DATA
       try:
           tdatas = NewLocalPro.objects.filter(is_delete=0).order_by('-published_at')
           counts = len(tdatas)
           datas = tdatas[startPos:endPos]
           pages = counts/ONE_PAGE_DATA
           remainCounts = counts%ONE_PAGE_DATA
           if remainCounts > 0:
               pages += 1
           err_msg = [0,'']
           #logger.info(str([key,data[key] for key in data  for data in datas])+str(curPage))
       except Exception as e:
           err_msg = [1,'Databse connect failed\n'+str(e)]
           logger.error('Databse connect failed. '+str(e))
    else:
       err_msg = [1,'不支持的请求']
       logger.error('不支持的请求')
    return render_to_response('synclocal.html',
                          {'username': username, 'datas': datas,'totalPage':pages,'curPage':curPage, 'err_msg': err_msg})



def addmultitag(request):
    tag_env = 'default'
    username = request.session.get('username')
    if request.method == 'POST':
        data = request.POST
        feurl = data['feurl'].strip()
        fetag = data['fetag'].strip()
        beurl = data['beurl'].strip()
        betag = data['betag'].strip()
        tagenv = data['genv'].strip()
        datas=OrderedDict()
        datas['be']={'url':beurl,'tag':betag}
        datas['fe']={'url':feurl,'tag':fetag}
        if tagenv == 'pro':
            tag_env=2
        else:
            tag_env=1
        pro_name = beurl.split(':')[1].split('.')[0].split('/')[1]
        pro_sign = hashlib.md5(pro_name+time.strftime('%Y%m%d%H%M%S', time.localtime())).hexdigest()
        ##获取branch
        if fetag and betag:
            if betag == '0':
                betag = 'master'
            if fetag == '0':
                fetag = 'master'
            querysetlist=[]
            for dk in datas.keys():
                try:
                    if Docker.objects.get(tag_url=datas[dk]['url'],code_branch=datas[dk]['tag'], tag_env=tag_env,pro_name=pro_name,is_delete=0):
                        #logger.info(Docker.objects.get(tag_url=datas[dk]['url'],code_branch=datas[dk]['tag'], tag_env=tag_env,pro_name=pro_name,is_delete=0).__dict__)
                        msg = '%s of %s on %s already exist' % (datas[dk]['tag'], datas[dk]['url'], tagenv)
                        request.session['err'] = msg
                        logger.info('%s of %s on %s already exist' % (datas[dk]['tag'], datas[dk]['url'], tagenv))
                        return HttpResponseRedirect('/publish/addmultitag/?genv=default')
                except:
                    querysetlist.append(Docker(tag_url=datas[dk]['url'],code_branch=datas[dk]['tag'], tag_env=tag_env,pro_name=pro_name,pro_sign=pro_sign,tag_type=dk,pro_type=2))
            try:
                Docker.objects.bulk_create(querysetlist)
                msg='Add %s successfully' % datas['be']['url']
                datas = Docker.objects.raw('select f.id,f.pro_name,f.code_branch as fbranch,b.code_branch as bbranch,f.created_at from publishs_docker f left join publishs_docker b on f.pro_sign=b.pro_sign where f.tag_env=%d and f.deploy_stat=0 and b.deploy_stat=0 and f.is_delete=0 and b.is_delete=0 group by f.created_at' % tag_env)
            except Exception as e:
                msg = 'Add %s of %s on %s failed' % (datas['be']['tag'], datas['be']['url'], tagenv)
                logger.error('Add %s of %s on %s failed' % (datas['be']['tag'],datas['be']['url'], tagenv)+str(e))
                request.session['err'] = msg
                return HttpResponseRedirect('/publish/addmultitag/?genv=default')
        else:
            request.session['err'] = '版本未指定，添加失败'
            logger.error('版本未指定，添加失败')
            return HttpResponseRedirect('/publish/addmultitag/?genv=default')
    else:
        if request.GET.has_key('genv') and request.GET['genv'] != 'default':
            datas = Docker.objects.raw('select f.id,f.pro_name,f.code_branch as fbranch,b.code_branch as bbranch,f.created_at from publishs_docker f left join publishs_docker b on f.pro_sign=b.pro_sign where tag_env='+tag_env+' and f.deploy_stat=0 and b.deploy_stat=0 and f.is_delete=0 and b.is_delete=0 group by f.created_at')
        else:
            datas = Docker.objects.raw('select f.id,f.pro_name,f.code_branch as fbranch,b.code_branch as bbranch,f.created_at from publishs_docker f left join publishs_docker b on f.pro_sign=b.pro_sign where f.deploy_stat=0 and b.deploy_stat=0 and f.is_delete=0 and b.is_delete=0 group by f.created_at order by f.created_at desc')
        msg=''
    if request.session.has_key('err'):
        err_msg = [1, request.session['err']]
        del request.session['err']
    else:
        err_msg = [0, msg]
    return render_to_response('addmultitag.html',
                              {'username': username, 'datas': datas, 'err_msg': err_msg})
def synccustom(request):
    username = request.session.get('username')
    logger.info(username)
    if request.method == 'GET':
       ONE_PAGE_DATA = 10 
       try:
           curPage = int(request.GET.get('curPage','1'))
           pageType = str(request.GET.get('pageType',''))
       except ValueError:
           curPage = 1 
           pageType = ''
       if pageType == 'pageDown':
          curPage += 1
       elif pageType == 'pageUp':
          curPage -= 1
       startPos = (curPage - 1) * ONE_PAGE_DATA
       endPos = startPos + ONE_PAGE_DATA
       try:
           tdatas = CustomPro.objects.filter(is_delete=0).exclude(pro_type=1).order_by('-build_at')
           counts = len(tdatas)
           datas = tdatas[startPos:endPos]
           pages = counts/ONE_PAGE_DATA
           remainCounts = counts%ONE_PAGE_DATA
           if remainCounts > 0:
               pages += 1
           err_msg = [0,'']
           #logger.info(str([key,data[key] for key in data  for data in datas])+str(curPage))
       except Exception as e:
           err_msg = [1,'Databse connect failed\n'+str(e)]
           logger.error('Databse connect failed. '+str(e))
    else:
       err_msg = [1,'不支持的请求']
       logger.error('不支持的请求')
    return render_to_response('synccustom.html',
                          {'username': username, 'datas': datas,'totalPage':pages,'curPage':curPage, 'err_msg': err_msg})


def pushdocker(request):
    username = request.session.get('username')
    if  request.method == 'GET':
        ONE_PAGE_DATA = 10 
        try:
            curPage = int(request.GET.get('curPage','1'))
            pageType = str(request.GET.get('pageType',''))
        except ValueError: 
            curPage = 1 
            pageType = ''
        if pageType == 'pageDown':
           curPage += 1
        elif pageType == 'pageUp': 
           curPage -= 1
        startPos = (curPage - 1) * ONE_PAGE_DATA
        endPos = startPos + ONE_PAGE_DATA

        if request.GET.items():
            if 'id' in request.GET.items()[0] and 'tenv' in request.GET.items()[1]:
                tid = request.GET['id']
                tag_env = request.GET['tenv']
                if tag_env == 'pro':
                    tag_env=2
                elif tag_env == 'test' or tag_env == 'testing2':
                    tag_env=1
                else:
                    tag_env=0
                if tag_env:
                    datas=Docker.objects.raw('select f.id,f.pro_name,f.code_branch as fe_branch,b.code_branch as be_branch,f.build_at from publishs_docker f left join publishs_docker b on f.pro_sign=b.pro_sign where b.pro_sign="%s" and f.is_delete=0 and b.is_delete=0 and and b.build_stat=1 and b.tag_env=%d group by b.pro_sign' % (tid,tag_env))
                else:
                    datas=Docker.objects.raw('select f.id,f.pro_name,f.code_branch as fe_branch,b.code_branch as be_branch,f.created_at from publishs_docker f left join publishs_docker b on f.pro_sign=b.pro_sign where b.pro_sign="%s"  and f.is_delete=0 and b.is_delete=0 and b.build_stat=1 group by b.pro_sign' % (tid))
            elif 'tenv' in request.GET.items()[0]:
                tag_env = request.GET['tenv'].strip()
                if tag_env == 'default':
                    datas = Docker.objects.raw('select f.id,f.pro_name,f.code_branch as fe_branch,b.code_branch as be_branch,f.build_at from publishs_docker f left join publishs_docker b on f.pro_sign=b.pro_sign where f.is_delete=0 and b.is_delete=0 and b.build_stat=1 group by b.pro_name,b.tag_env,b.build_at order by b.build_at desc')
                elif tag_env == 'test':
                    datas = Docker.objects.raw('select * from (select * from publishs_docker where tag_env=1 order by build_at desc) as t  group by t.tag_url,t.tag_env,t.code_branch order by t.build_at desc')
                else:
                    datas = Docker.objects.raw(
                        'select * from (select * from publishs_docker where tag_env=2 order by build_at desc) as o  group by o.tag_url,o.tag_env,o.code_branch order by o.build_at desc')
            else:
                tag_env = 'default'
                datas = Docker.objects.raw('select * from (select * from publishs_docker order by published_at desc) as d group by d.tag_url,d.tag_env,d.code_branch order by d.id desc')
        err_msg = [0, '']
    else:
        err_msg = [1,'request method not support']
    tdatas = Docker.objects.raw('select * from pbs_test.docker_page order by build_at desc')
    counts = len(list(tdatas))
    datas = list(tdatas)[startPos:endPos]
    pages = counts/ONE_PAGE_DATA
    remainCounts = counts%ONE_PAGE_DATA
    if remainCounts > 0:
        pages += 1
    return render_to_response('syncdocker.html',
                          {'username': username, 'datas': datas,'totalPage':pages,'curPage':curPage, 'err_msg': err_msg, 'selenv': tag_env})

def rebuild(request):
    if request.method == 'GET':
        sid=request.GET['id']
        Docker.objects.filter(pro_sign=sid).update(build_stat=0,deploy_stat=0,tag_env=1)
    return HttpResponseRedirect('/publish/buildimg/')

    
