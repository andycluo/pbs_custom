# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BuildHistory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('build_sign', models.CharField(default='', help_text='\u6784\u5efaID', max_length=64)),
                ('build_tag', models.CharField(default='', max_length=128)),
                ('build_at', models.CharField(default='', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='CustomPro',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('pro_name', models.CharField(default='', max_length=32)),
                ('pro_sign', models.CharField(default='', max_length=64)),
                ('tag_url', models.CharField(max_length=128)),
                ('code_branch', models.CharField(default='', max_length=128)),
                ('pro_type', models.IntegerField(default=1, help_text='1\u3001fe 2\uff1abase 3: ats')),
                ('tag_env', models.IntegerField(default=1, help_text='1\uff1a\u6d4b\u8bd5\u73af\u5883 2\uff1a\u751f\u4ea7\u73af\u5883')),
                ('dockerimg', models.CharField(default='', max_length=128)),
                ('build_stat', models.IntegerField(default=0, help_text='0:\u672a\u6784\u5efa 1:\u6784\u5efa\u6210\u529f 2:\u6784\u5efa\u5931\u8d25')),
                ('deploy_stat', models.IntegerField(default=0, help_text='0:\u5df2\u6dfb\u52a0,\u5f85\u63d0\u6d4b 1\uff1a\u5df2\u63d0\u6d4b 2\uff1a\u5df2\u4e0a\u7ebf 3:\u63d0\u6d4b\u5931\u8d25 4:\u4e0a\u7ebf\u5931\u8d25')),
                ('is_delete', models.IntegerField(default=0, help_text='0\u3001\u672a\u5220\u9664 1\uff1a\u5220\u9664')),
                ('last_published_tag', models.CharField(default='', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('build_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6784\u5efa\u65f6\u95f4')),
                ('published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u540c\u6b65\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='DeployHistory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('tag', models.CharField(default='', max_length=128)),
                ('deploy_env', models.CharField(default='test', help_text='docker\u90e8\u7f72\u73af\u5883', max_length=8)),
                ('deploy_at', models.CharField(default='', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Docker',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('pro_name', models.CharField(default='', max_length=32)),
                ('pro_sign', models.CharField(default='', max_length=64)),
                ('tag_url', models.CharField(max_length=128)),
                ('code_branch', models.CharField(default='', max_length=128)),
                ('pro_type', models.IntegerField(default=1, help_text='1\u3001\u72ec\u7acb 2\uff1a\u7efc\u5408 3: app')),
                ('tag_type', models.CharField(help_text='be\uff1a\u540e\u7aef fe\uff1a\u524d\u7aef st\uff1a\u72ec\u7acb', max_length=16)),
                ('tag_env', models.IntegerField(default=1, help_text='1\uff1a\u6d4b\u8bd5\u73af\u5883 2\uff1a\u751f\u4ea7\u73af\u5883')),
                ('dockerimg', models.CharField(default='', max_length=128)),
                ('build_stat', models.IntegerField(default=0, help_text='0:\u672a\u6784\u5efa 1:\u6784\u5efa\u6210\u529f 2:\u6784\u5efa\u5931\u8d25')),
                ('deploy_stat', models.IntegerField(default=0, help_text='0:\u5df2\u6dfb\u52a0,\u5f85\u63d0\u6d4b 1\uff1a\u5df2\u63d0\u6d4b 2\uff1a\u5df2\u4e0a\u7ebf 3:\u63d0\u6d4b\u5931\u8d25 4:\u4e0a\u7ebf\u5931\u8d25 5:\u63d0\u6d4b\u5230test3 6:\u90e8\u7f72\u5230test3\u5931\u8d25')),
                ('is_delete', models.IntegerField(default=0, help_text='0\u3001\u672a\u5220\u9664 1\uff1a\u5220\u9664')),
                ('last_published_tag', models.CharField(default='', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('build_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6784\u5efa\u65f6\u95f4')),
                ('published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u540c\u6b65\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='Dockerconf',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('denv', models.CharField(default='', max_length=8)),
                ('pro_name', models.CharField(default='', max_length=32)),
                ('hosts', models.TextField(default='', blank=True)),
                ('deploy_list', models.TextField(default='', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Gmconf',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('work_name', models.CharField(max_length=128)),
                ('gm_server', models.CharField(max_length=15)),
                ('gm_port', models.IntegerField(default=4730)),
                ('gm_env', models.CharField(max_length=10)),
                ('status', models.IntegerField(default=0, help_text='0:\u5df2\u6dfb\u52a0,\u5f85\u63a8\u9001 1\uff1a\u5df2\u63a8\u9001')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u540c\u6b65\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='NewLocalPro',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('proname', models.CharField(default='', max_length=128)),
                ('pro_sign', models.CharField(default='', max_length=64)),
                ('svrname', models.CharField(default='', max_length=32)),
                ('tag_url', models.CharField(max_length=128)),
                ('code_branch', models.CharField(default='', max_length=128)),
                ('dockerimg', models.CharField(default='', max_length=128)),
                ('build_stat', models.IntegerField(default=0, help_text='0:\u672a\u6784\u5efa 1:\u6784\u5efa\u6210\u529f 2:\u6784\u5efa\u5931\u8d25')),
                ('deploy_stat', models.IntegerField(default=0, help_text='0:\u5df2\u6dfb\u52a0,\u5f85\u63d0\u6d4b 1\uff1a\u5df2\u63d0\u6d4b 2:\u63d0\u6d4b\u5931\u8d25')),
                ('is_delete', models.IntegerField(default=0, help_text='0\u3001\u672a\u5220\u9664 1\uff1a\u5220\u9664')),
                ('last_published_version', models.CharField(default='', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u540c\u6b65\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='Tagconf',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('tag_url', models.CharField(max_length=128)),
                ('tag_branch', models.CharField(default='', max_length=32)),
                ('pro_name', models.CharField(default='', max_length=32)),
                ('tag_env', models.CharField(max_length=10)),
                ('status', models.IntegerField(default=0, help_text='0:\u5df2\u6dfb\u52a0,\u5f85\u63d0\u6d4b 1\uff1a\u5df2\u63d0\u6d4b\uff0c\u5f85\u4e0a\u7ebf 2\uff1a\u5df2\u4e0a\u7ebf 3: \u90e8\u7f72\u5230testing3')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6dfb\u52a0\u65f6\u95f4')),
                ('t_published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6d4b\u8bd5\u73af\u5883\u540c\u6b65\u65f6\u95f4')),
                ('t3_published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u6d4b\u8bd5\u73af\u58833\u540c\u6b65\u65f6\u95f4')),
                ('last_published_tag', models.CharField(default='', max_length=50)),
                ('t_last_published_tag', models.CharField(default='', max_length=50)),
                ('t3_last_published_tag', models.CharField(default='', max_length=50)),
                ('published_at', models.DateTimeField(auto_now_add=True, verbose_name='\u540c\u6b65\u65f6\u95f4')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('pwd', models.CharField(max_length=1024)),
                ('level', models.IntegerField(default=1)),
            ],
        ),
    ]
