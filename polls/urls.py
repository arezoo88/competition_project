from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    path('vote/', views.vote, name='vote'),

]