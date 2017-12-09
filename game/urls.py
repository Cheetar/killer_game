from django.conf.urls import url

from . import views

app_name = 'game'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_user, name='login_user'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^rules/$', views.rules, name='rules'),
    url(r'^living/$', views.living, name='living'),
    url(r'^deathnote/$', views.deathnote, name='deathnote'),
    # ex: /profile/qr/2b3ac424...2dc1/
    url(r'^profile/qr/(?P<signature>.+)/$', views.profile_qr, name='profile_qr'),
    # ex: /profile/2b3ac424...2dc1/
    url(r'^profile/(?P<signature>.+)/$', views.profile, name='profile'),
    # ex: /kill/382abf2c2...23d/
    url(r'^kill/(?P<kill_signature>[0-9a-f]+)/$', views.kill, name='kill'),
    url(r'^kill/$', views.manual_kill, name='manual_kill'),
    url(r'^statistics/$', views.statistics, name='statistics')
]
