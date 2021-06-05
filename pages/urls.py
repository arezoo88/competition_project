from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('honors/list', views.honors_list, name='honors_list'),
    path('honors/<int:honors_id>',views.honors_detail,name='honors_detail'),
    path('filter_gender', views.filter_gender, name='filter_gender'),
]