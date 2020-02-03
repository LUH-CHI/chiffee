from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('accounts/edit/', views.edit_accounts, name='edit-accounts'),
    path('accounts/', views.view_accounts, name='view-accounts'),
    path('login/',
         auth_views.LoginView.as_view(template_name='chiffee/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='chiffee:index'),
         name='logout'),
    path('products/edit/', views.edit_products, name='edit-products'),
    path('products/restore/', views.restore_products, name='restore-products'),
    path('products/', views.view_products, name='view-products'),
    path('purchases/all/', views.view_all_purchases, name='view-all-purchases'),
    path('purchases/cancel/<str:key>/',
         views.cancel_purchases,
         name='cancel-purchases'),
    path('purchases/confirm/',
         views.confirm_purchases,
         name='confirm-purchases'),
    path('purchases/make/', views.make_purchases, name='make-purchases'),
    path('purchases/personal/',
         views.view_my_purchases,
         name='view-my-purchases'),
    path('', views.index, name='index'),
]
