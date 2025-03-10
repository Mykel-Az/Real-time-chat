from django.forms import ModelForm
from django import forms
from .models import *


class ChatMessageCreateForm(ModelForm):

    class Meta:
        model = GroupMessage
        fields = ['content']
        widgets ={
            'content': forms.TextInput(attrs={
                'id': 'chat-message-input',
                'class': 'chat-input',
                'placeholder': "Add message...", 
                'autofocus':True})
        }


class NewGroupchatCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox checkbox-primary'  # DaisyUI checkbox class
        }),
        help_text="Select members to add to the group"
    )

    is_private = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Check this to make group private",
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox checkbox-primary'  # DaisyUI checkbox class
        }),
        label="Private Group"
    )

    class Meta:
        model = GroupChatRoom
        fields = ['groupchat_name', 'members', 'is_private']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'placeholder': 'Add name...',
                'class': 'input input-bordered w-full max-w-lg',  # DaisyUI input class
                'maxlength': '300',
                'autofocus': True
            }),
        }
        labels = {
            'groupchat_name': 'Group Name'
        }