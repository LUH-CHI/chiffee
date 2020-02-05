from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('accounts/', views.accounts, name='accounts'),
    path('login/',
         auth_views.LoginView.as_view(template_name='chiffee/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='chiffee:index'),
         name='logout'),
    path('products/', views.products, name='products'),
    path('purchases/all/', views.view_all_purchases, name='view-all-purchases'),
    path('purchases/cancel/<str:key>/',
         views.cancel_purchase,
         name='cancel-purchase'),
    path('purchases/make/', views.make_purchase, name='make-purchase'),
    path('purchases/personal/',
         views.view_my_purchases,
         name='view-my-purchases'),
    path('', views.index, name='index'),
]
