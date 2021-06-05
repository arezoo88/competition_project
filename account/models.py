from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    def personal_image_filename(self, filename):
        return f'photos/users/{filename}'

    gender = models.IntegerField(default=0)
    birth_date = models.CharField(max_length=12)
    phone = models.CharField(max_length=20)
    personal_image = models.ImageField(upload_to=personal_image_filename, blank=True)
    national_document_image = models.ImageField(upload_to=personal_image_filename, blank=True)
    address = models.CharField(max_length=500)
    postal_code = models.CharField(max_length=30, blank=True)
    activate_status = models.BooleanField(default=False)
    interest = models.IntegerField(default=0)  #0 judo / 1 jujitso / 2 hardo


#


class Profile_Judo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qform_document = models.ImageField(upload_to='photos/users/Judo/', blank=True)
    club_name = models.CharField(max_length=100, blank=True)
    coach_name = models.CharField(max_length=100, blank=True)
    position = models.IntegerField(default=0)


class Profile_Jujitso(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qform_document = models.ImageField(upload_to='photos/users/Jujitso/', blank=True)
    club_name = models.CharField(max_length=100, blank=True)
    coach_name = models.CharField(max_length=100, blank=True)
    position = models.IntegerField(default=0)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # signal
def update_user_Profile_Judo(sender, instance, created, **kwargs):
    if created:
        Profile_Judo.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # signal
def update_user_Profile_Jujitso(sender, instance, created, **kwargs):
    if created:
        Profile_Jujitso.objects.create(user=instance)
