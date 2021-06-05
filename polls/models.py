from django.db import models
from account.models import User
from django.conf import settings


class Question(models.Model):
    title = models.CharField(max_length=50)
    question_text = models.CharField(max_length=400)
    create_date = models.CharField(max_length=30, default='-')
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text




class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=50)

    def __str__(self):
        return self.choice_text


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    vote = models.IntegerField(default=1)
