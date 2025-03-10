from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import SignupForm
from .models import *

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

class ClienteleUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True )
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ( "first_name", "last_name", "username", "email")

        


class AccountsForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model  = User
        fields = ("username", "first_name", "last_name", "phone", "email", "password")



# class PasswordChangingForm(PasswordChangeForm):
#     old_password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
#     new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
#     new_password2 =forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))

#     class Meta:
#         model = User
#         fields = ["old_password", "new_password1", "new_pasword2"]



class ProfileForm(forms.ModelForm):
    bio = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
    )
    website = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
    )
    display_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    class Meta:
        model = UserProfile
        fields = ["bio", "website", "display_picture", "country", "gender", "dob"]
        widgets = {
            "gender": forms.Select(attrs={'class': 'form-control'}),
            "country": CountrySelectWidget(attrs={'class': 'form-control'}),
        }