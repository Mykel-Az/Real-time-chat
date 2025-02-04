from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('chathome', chathome, name='chathome'),
    # path('chat/<str:room_name>/', room, name = 'chat'),
]