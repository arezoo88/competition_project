from django.urls import path
from . import views
app_name = 'competition'
urlpatterns = [

    # path('competitions/enable/list',views.competitions_enable_list,name='enable_list'),
    path('gallery',views.gallery_list,name='gallery_list'),
    path('competition_list',views.competition_list,name='competition_list'),
    path('ranking_list',views.ranking_list,name='ranking_list'),
    path('filter_competition_list',views.filter_competition_list,name='filter_competition_list'),
    path('filter_competition_list',views.filter_competition_list,name='filter_competition_list'),
    path('filter_competition_list',views.filter_competition_list,name='filter_competition_list'),
    path('register/register_in_competition/<str:cmpt_id>',views.register_in_competition,name='register_in_competition'),
    path('register/final_register',views.final_register,name='final_register'),
    path('register/',views.register,name='register'),
]