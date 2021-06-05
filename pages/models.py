from django.db import models


class Company_Info(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100,blank=True)
    logo_img = models.ImageField(upload_to='photos/company',null=True,blank=True)
    manager_name = models.CharField(max_length=100,blank=True)
    phone = models.CharField(max_length=100,blank=True)
    fax = models.CharField(max_length=100,blank=True)
    address = models.CharField(max_length=300,blank=True)
    banner_img = models.ImageField(upload_to='photos/company',null=True,blank=True)
    about = models.TextField(blank=True)
