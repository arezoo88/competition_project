from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('account.urls')),
    path('ckeditor/',include('ckeditor_uploader.urls')),
    path('competition/',include('competition.urls')),
    path('news/',include('news.urls')),
    path('',include('pages.urls')),
    path('panel/',include('panel.urls')),
    path('polls/',include('polls.urls')),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
