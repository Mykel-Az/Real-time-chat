from django.urls import path
from .views import *

urlpatterns = [
    path('', chat_view, name='chats'),
    # path('chathome', chathome, name='chathome'),
    path('groupchat/<str:room_code>/', groupchat, name='chatroom'),
    path('creategroup', creategroupchat, name='creategroupchat'),
    path('directchat/<str:room_code>/', directchat, name='directchat'),
    path('directchat/create/<str:username>/', privatechat, name='privatechat')
]