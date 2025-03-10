from django.urls import path
from .consumers import *


websocket_urlpatterns = [
        path('ws/chat/groupchat/<str:room_code>/', GroupChatConsumer.as_asgi()),
        path('ws/chat/directchat/<str:room_code>/', PrivateChatConsumer.as_asgi()),
]