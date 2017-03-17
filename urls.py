from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [    
    url(r'^login/$', auth_views.login, {'template_name': 'chiffee/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^home/$', views.showhistory, name='home'),

    url(r'^$', views.products, name='index'),
    url(r'^(?P<productID>[a-z,A-Z,\s]+)/$', views.users, name='users'),
    url(r'^(?P<productID>[a-z,A-Z,\s]+)/(?P<userID>[a-z,A-Z,\s]+)/$', views.confirm, name='confirm'),
    url(r'^(?P<productID>[a-z,A-Z,\s]+)/(?P<userID>[a-z,A-Z,\s]+)/(?P<count>[0-9]+)$', views.confirmed, name='confirmed'),
    
]
