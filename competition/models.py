from django.db import models
from account.models import User

import os





class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    small_img = models.ImageField(upload_to='photos/gallery')
    big_img = models.ImageField(upload_to='photos/gallery')
    description = models.TextField()
    is_published = models.BooleanField(default=True)


class Weight_Classification(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)


class Competition(models.Model):
    id = models.AutoField(primary_key=True)
    cmp_id = models.IntegerField(default=0)
    poster_image = models.ImageField(upload_to='photos/competition/', blank=True)
    bakhshname_image = models.ImageField(upload_to='photos/competition/', blank=True)
    title = models.CharField(max_length=100)
    subtitle = models.IntegerField(default=3)
    gender = models.IntegerField(default=0)
    user_from_birtday = models.CharField(max_length=20)
    user_to_birthday = models.CharField(max_length=20)
    weight = models.ForeignKey(Weight_Classification, on_delete=models.CASCADE)
    register_from = models.CharField(max_length=20)
    register_to = models.CharField(max_length=20)
    competition_date = models.CharField(max_length=20)
    capacity = models.CharField(max_length=100)
    create_date = models.CharField(max_length=20, default='-')
    is_published = models.BooleanField(default=True)


class Rank_Detail(models.Model):
    id = models.AutoField(primary_key=True)
    place = models.IntegerField(default=0)
    point = models.IntegerField(default=0)
    cmp_id = models.ForeignKey(Competition, on_delete=models.CASCADE)


class User_In_Competition(models.Model):
    def image_filename(self, filename):
        return f'photos/competition/{self.cid_id}/users/{self.uid_id}/{filename}'

    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    image = models.ImageField(upload_to=image_filename)
    cid = models.ForeignKey(Competition, on_delete=models.CASCADE)
    place_id = models.ForeignKey(Rank_Detail, on_delete=models.CASCADE, blank=True)
    reject_status = models.BooleanField(default=False)
    reject_cause = models.CharField(max_length=500, blank=True)


class Honors(models.Model):
    full_name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='honors/image/')
    grade = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)


class Honors_Files(models.Model):
    honors_id = models.ForeignKey(Honors, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    file = models.FileField(upload_to='honors/files/')

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension
