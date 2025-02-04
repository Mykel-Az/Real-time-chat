from django.forms import ModelForm
from django import forms
from .models import *

class ChatMessageCreateForm(ModelForm):

    class Meta:
        models = GroupMessage
        fields = ['content']
        widgets ={
            'content': forms.TextInput(attrs={'placeholder': "Add message...", 'autofocus':True})
        }


# class NewGroupForm