from django.urls import path,include
from . import views
app_name = 'panel'
urlpatterns = [

    path('panel_profile',views.panel_profile,name='panel_profile'),
    path('panel_profile/panel_profile_edit',views.panel_profile_edit,name='panel_profile_edit'),
    path('panel_profile/panel_profile_change_pass',views.panel_profile_change_pass,name='panel_profile_change_pass'),
    path('panel_dashboard',views.panel,name='panel_dashboard'),
    path('panel_company',views.panel_company,name='panel_company'),

    #gallery
    path('panel_gallery/panel_gallery_list', views.panel_gallery_list, name='panel_gallery_list'),
    path('panel_gallery/panel_gallery_add', views.panel_gallery_add, name='panel_gallery_add'),
    path('panel_gallery/panel_gallery_enable', views.panel_gallery_enable, name='panel_gallery_enable'),
    path('panel_gallery/panel_gallery_delete', views.panel_gallery_delete, name='panel_gallery_delete'),
    path('panel_gallery/panel_gallery_edit/<int:image_id>', views.panel_gallery_edit, name='panel_gallery_edit'),

    #honors
    path('panel_honor/panel_honor_list', views.panel_honors_list, name='panel_honors_list'),
    path('panel_honor/panel_honors_add', views.panel_honors_add, name='panel_honors_add'),
    path('panel_honor/panel_honors_edit/<int:honors_id>', views.panel_honors_edit, name='panel_honors_edit'),
    path('panel_honor/panel_honors_delete', views.panel_honors_delete, name='panel_honors_delete'),
    path('panel_honor/panel_honors_enable', views.panel_honors_enable, name='panel_honors_enable'),

    #survey
    path('panel_survey/panel_survey_list', views.panel_survey_list, name='panel_survey_list'),
    path('panel_survey/panel_survey_add', views.panel_survey_add, name='panel_survey_add'),
    path('panel_survey/panel_survey_enable', views.panel_survey_enable, name='panel_survey_enable'),
    path('panel_survey/panel_survey_delete', views.panel_survey_delete, name='panel_survey_delete'),
    path('panel_survey/panel_survey_edit/<int:survey_id>', views.panel_survey_edit, name='panel_survey_edit'),
    path('panel_survey/panel_items_edit/<int:survey_id>', views.panel_items_edit, name='panel_items_edit'),

    #news urls
    path('panel_news/panel_news_add',views.panel_news_add,name='panel_news_add'),
    path('panel_news/panel_news_list',views.panel_news_list,name='panel_news_list'),
    path('panel_news/panel_news_delete',views.panel_news_delete,name='panel_news_delete'),
    path('panel_news/panel_news_edit/<int:news_id>',views.panel_news_edit,name='panel_news_edit'),
    path('panel_news/panel_news_enable', views.panel_news_enable, name='panel_news_enable'),
    path('panel_news/add_category_news', views.add_category_news, name='add_category_news'),
    path('panel_news/select_cat_news', views.select_cat_news, name='select_cat_news'),
    path('panel_news/delete_category', views.delete_category, name='delete_category'),
    path('panel_news/list_category', views.list_category, name='list_category'),
    path('panel_news/delete_cat_news', views.delete_cat_news, name='delete_cat_news'),
    path('panel_news/category_selected', views.category_selected, name='category_selected'),


    #users urls
    path('panel_users/panel_user_list', views.panel_user_list, name='panel_user_list'),
    path('panel_users/panel_user_search', views.panel_user_search, name='panel_user_search'),
    path('panel_users/panel_user_edit/<int:user_id>', views.panel_user_edit, name='panel_user_edit'),
    path('panel_users/panel_user_enable', views.panel_user_enable, name='panel_user_enable'),
    # path('delete_user/<int:user_id>', views.delete_user, name='delete_user'),

    #competition url
    path('panel_competition/panel_competition_list',views.panel_competition_list,name='panel_competition_list'),
    path('panel_competition/panel_competition_add',views.panel_competition_add,name='panel_competition_add'),
    path('panel_competition/panel_competition_edit/<int:cmp_id>',views.panel_competition_edit,name='panel_competition_edit'),
    path('panel_competition/panel_competition_enable',views.panel_competition_enable,name='panel_competition_enable'),
    path('panel_competition/panel_competition_delete',views.panel_competition_delete,name='panel_competition_delete'),
    path('panel_competition/panel_competition_user/<int:cmp_id>',views.panel_competition_user,name='panel_competition_user'),
    path('panel_competition/panel_user_in_competition_enable',views.panel_user_in_competition_enable,name='panel_user_in_competition_enable'),


    path('panel_competition/panel_user_reject',views.panel_user_reject,name='panel_user_reject'),
    path('panel_competition/update_weight',views.update_weight,name='update_weight'),
    path('panel_competition/point_save',views.point_save,name='point_save'),
    # path('panel_competition/update_age_and_weight',views.update_age_and_weight,name='update_age_and_weight'),


    # path('panel_competition/panel_user_in_competition_edit',views.panel_user_in_competition_edit,name='panel_user_in_competition_edit'),

    path('panel_competition/panel_competition_rank/<int:cmp_id>',views.panel_competition_rank,name='panel_competition_rank'),
    path('panel_competition/panel_competition_weight',views.panel_competition_weight,name='panel_competition_weight'),
    path('panel_competition/check_len_weight_table',views.check_len_weight_table,name='check_len_weight_table'),

]
