from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('home', home, name='home'),    
    path('accounts/signup', SignUpView.as_view(), name='account_signup'),
    path('profile/<int:pk>', user_profile, name ='user_profile'),
    path('profile/create', CreateProfile.as_view(), name='profile_create'),
    path('profile/<int:pk>/edit', edit_profile, name='profile_edit'),
    path('profile/<int:pk>/follow', follow, name='follow'),
    path('profile/<int:pk>/familiar', familiars, name='familiars'),
    path('accounts_settings', UserChange.as_view(), name='accounts_settings'),
]