from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField



class Category_News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=300)



class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category_News, on_delete=models.SET_NULL,blank=True,null=True)
    image_1 = models.ImageField(upload_to='photos/news/',blank=True)
    short_text = models.TextField(blank=True)
    description = RichTextUploadingField(blank=True,null=True,config_name='default')
    create_date = models.CharField(max_length=30,default='-')
    is_published = models.BooleanField(default=True)
    def __str__(self):
        return self.title



    def summery(self):
        return self.short_text

