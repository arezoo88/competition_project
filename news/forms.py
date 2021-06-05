from django.forms import ModelForm
from django import forms
from news.models import News


# Create the form class.
class NewsForm(ModelForm):
    class Meta:
        model = News

        fields = ['title', 'image_1', 'short_text', 'description']
        labels = {
            "description": 'متن',
        }
