# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    pwd = models.CharField(max_length=1024)
    level = models.IntegerField(default=1)
    # def __unicode__(self):
    #     return  self.name,self.pwd
class Gmconf(models.Model):
    id = models.AutoField(primary_key=True)
    work_name = models.CharField(max_length=128)
    gm_server = models.CharField(max_length=15)
    gm_port = models.IntegerField(default=4730)
    gm_env = models.CharField(max_length=10)
    status = models.IntegerField(default=0,help_text='0:已添加,待推送 1：已推送')
    created_at = models.DateTimeField('添加时间',auto_now_add=True)
    published_at = models.DateTimeField('同步时间',auto_now_add=True)
class Tagconf(models.Model):
    id = models.AutoField(primary_key=True)
    tag_url = models.CharField(max_length=128)
    tag_branch = models.CharField(max_length=32,default='')
    pro_name = models.CharField(max_length=32, default='')
    tag_env = models.CharField(max_length=10)
    status = models.IntegerField(default=0,help_text='0:已添加,待提测 1：已提测，待上线 2：已上线 3: 部署到testing3')
    created_at = models.DateTimeField('添加时间',auto_now_add=True)
    t_published_at = models.DateTimeField('测试环境同步时间',auto_now_add=True)
    t3_published_at = models.DateTimeField('测试环境3同步时间',auto_now_add=True)
    last_published_tag = models.CharField(default='',max_length=50)
    t_last_published_tag = models.CharField(default='',max_length=50)
    t3_last_published_tag = models.CharField(default='',max_length=50)
    published_at = models.DateTimeField('同步时间',auto_now_add=True)
class Docker(models.Model):
    id = models.AutoField(primary_key=True)
    pro_name = models.CharField(max_length=32, default='')
    pro_sign = models.CharField(max_length=64, default='')
    tag_url = models.CharField(max_length=128)
    code_branch = models.CharField(max_length=128,default='')
    pro_type = models.IntegerField(default=1,help_text='1、独立 2：综合 3: app')
    tag_type = models.CharField(max_length=16,help_text='be：后端 fe：前端 st：独立')
    tag_env = models.IntegerField(default=1,help_text='1：测试环境 2：生产环境')
    dockerimg = models.CharField(max_length=128, default='')
    build_stat = models.IntegerField(default=0,help_text='0:未构建 1:构建成功 2:构建失败')
    deploy_stat = models.IntegerField(default=0,help_text='0:已添加,待提测 1：已提测 2：已上线 3:提测失败 4:上线失败 5:提测到test3 6:部署到test3失败')
    is_delete = models.IntegerField(default=0,help_text='0、未删除 1：删除')
    last_published_tag = models.CharField(default='',max_length=32)
    created_at = models.DateTimeField('添加时间',auto_now_add=True)
    build_at = models.DateTimeField('构建时间',auto_now_add=True)
    published_at = models.DateTimeField('同步时间',auto_now_add=True)

class CustomPro(models.Model):
    id = models.AutoField(primary_key=True)
    pro_name = models.CharField(max_length=32, default='')
    pro_sign = models.CharField(max_length=64, default='')
    tag_url = models.CharField(max_length=128)
    code_branch = models.CharField(max_length=128,default='')
    pro_type = models.IntegerField(default=1,help_text='1、fe 2：base 3: ats')
    tag_env = models.IntegerField(default=1,help_text='1：测试环境 2：生产环境')
    dockerimg = models.CharField(max_length=128, default='')
    build_stat = models.IntegerField(default=0,help_text='0:未构建 1:构建成功 2:构建失败')
    deploy_stat = models.IntegerField(default=0,help_text='0:已添加,待提测 1：已提测 2：已上线 3:提测失败 4:上线失败')
    is_delete = models.IntegerField(default=0,help_text='0、未删除 1：删除')
    last_published_tag = models.CharField(default='',max_length=32)
    created_at = models.DateTimeField('添加时间',auto_now_add=True)
    build_at = models.DateTimeField('构建时间',auto_now_add=True)
    published_at = models.DateTimeField('同步时间',auto_now_add=True)
class NewLocalPro(models.Model):
    id = models.AutoField(primary_key=True)
    proname = models.CharField(max_length=128,default='')
    pro_sign = models.CharField(max_length=64, default='')
    svrname = models.CharField(max_length=32, default='')
    tag_url = models.CharField(max_length=128)
    code_branch = models.CharField(max_length=128,default='')
    dockerimg = models.CharField(max_length=128, default='')
    build_stat = models.IntegerField(default=0,help_text='0:未构建 1:构建成功 2:构建失败')
    deploy_stat = models.IntegerField(default=0,help_text='0:已添加,待提测 1：已提测 2:提测失败')
    is_delete = models.IntegerField(default=0,help_text='0、未删除 1：删除')
    last_published_version = models.CharField(default='',max_length=32)
    created_at = models.DateTimeField('添加时间',auto_now_add=True)
    published_at = models.DateTimeField('同步时间',auto_now_add=True)

class BuildHistory(models.Model):
    id = models.AutoField(primary_key=True)
    build_sign = models.CharField(max_length=64,default='',help_text='构建ID')
    build_tag = models.CharField(max_length=128, default='')
    build_at = models.CharField(max_length=32, default='')
class DeployHistory(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.CharField(max_length=128, default='')
    deploy_env = models.CharField(max_length=8, default='test',help_text='docker部署环境')
    deploy_at = models.CharField(max_length=32, default='')
class Dockerconf(models.Model):
    id = models.AutoField(primary_key=True)
    denv = models.CharField(max_length=8, default='')
    pro_name = models.CharField(max_length=32, default='')
    hosts = models.TextField(blank=True, default='')
    deploy_list = models.TextField(blank=True, default='')
