from django.conf.urls import url
from . import views,api

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^index/$', views.index, name='index'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^addgm/$', views.addgm, name='addgm'),
    url(r'^syncgm/$', views.syncgm, name='syncgm'),
    url(r'^syncgming/$', views.syncgming, name='syncgming'),
    url(r'^addlocal/$', views.addlocal, name='addlocal'),
    url(r'^synctag/$', views.synctag, name='synctag1'),
    url(r'^dockercfg/$', views.dockercfg, name='dockercfg'),
    url(r'^addtag2/$', views.addtag2, name='addtag2'),
    url(r'^addapp/$', views.addapp, name='addapp'),
    url(r'^addcustom/$', views.addcustom, name='addcustom'),
    url(r'^deployfe/$', views.syncfe, name='deployfe'),
    url(r'^deploycustom/$', views.synccustom, name='deploycustom'),
    url(r'^deploylocal/$', views.synclocal, name='deploylocal'),
    url(r'^addmultitag/$', views.addmultitag, name='addmultitag'),
    url(r'^buildimg/$', views.buildimg, name='buildimg'),
    url(r'^rebuild/$', views.rebuild, name='rebuild'),
    url(r'^pushdocker/$', views.pushdocker, name='pushdocker'),
    url(r'^api/syncconf/$', api.syncconf, name='syncconf'),
    url(r'^api/delDocConf/$', api.delDocConf, name='delDocConf'),
    url(r'^api/buildimg/$', api.buildimg, name='buildimg'),
    url(r'^api/buildcustom/$', api.buildcustom, name='buildcustom'),
    url(r'^api/asyncdocker/$', api.asyncdocker, name='asyncdocker'),
    url(r'^rollback/$', views.rollback, name='rollback1'),
    url(r'^api/asynctag/$', api.asynctag, name='asynctag2'),
    url(r'^api/asynccustomfe/$', api.asynccustomfe, name='asynccustomfe'),
    url(r'^api/asynccustom/$', api.asynccustom, name='asynccustom'),
    url(r'^api/asynclocal/$', api.asynclocal, name='asynclocal'),
    url(r'^api/asynctag2/$', api.asynctag2, name='asynctag3'),
    url(r'^api/rollback/$', api.rollback, name='rollback2'),
    url(r'^api/aaa/$', api.aaa, name='aaa'),
]