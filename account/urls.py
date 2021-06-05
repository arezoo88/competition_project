from django.urls import path
from . import views

app_name = 'account'


urlpatterns = [
    path('register',views.register,name='register'),
    path('confirm',views.confirm,name='confirm'),
    path('login', views.login, name='login'),
    path('logout',views.logout,name='logout'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('resend_sms',views.resend_sms_code,name='resend_sms_code'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('reset_password',views.reset_password,name='reset_password'),
]


