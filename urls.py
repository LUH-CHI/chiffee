from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(), {'template_name': 'chiffee/login.html'}, name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    url(r'^home/$', views.showoverview, name='home'),
    url(r'^money/$', views.showmoney, name='money'),
    url(r'^prod/$', views.showproducts, name='prod'),
    url(r'^history/$', views.showhistory, name='history'),

    url(r'^$', views.products, name='index'),
    url(r'^(?P<productID>[a-z,A-Z,\s,\(,\),\,,0-9,\&]+)/$', views.users, name='users'),
    url(r'^(?P<productID>[a-z,A-Z,\s,\(,\),\,,0-9,\&]+)/(?P<userID>[a-z,A-Z,\s]+)/$', views.confirm, name='confirm'),
    url(r'^(?P<productID>[a-z,A-Z,\s,\(,\),\,,0-9,\&]+)/(?P<userID>[a-z,A-Z,\s]+)/(?P<count>[0-9]+)$', views.confirmed, name='confirmed'),

]
