import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import *


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.chatroom = get_object_or_404(GroupChatRoom, room_code=self.room_name)

        # join room group
        await self.channel_layer.group_add(
            self.chatroom,
            self.channel_name
        )

        # Add user to users_online
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.chatroom,
            self.channel_name
        )

        # reomve user from online_user
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()


        # receive message from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json['message']

        message = GroupMessage.objects.create(content = text, sender = self.user, room=self.chatroom)

        # send message to room group
        await self.channel_layer.group_send(
            self.chatroom,
            {
                'type': 'chat_message',
                'message': message
            }
        )

         # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        text = GroupMessage.objects.get(id=message)
        # context = {
        #     'message': message,
        #     'user': self.user,
        # }
        # html = render_to_string("partials/chat_message_p.html", context=context)
        # self.send(text_data=html)
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': text
        }))

    async def update_online_count(self):
        online_count = self.chatroom.users_online.count()

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        await self.channel_layer.group_send(self.room_name, event)

    async  def online_count_handler(self, event):
        online_count = event['online_count']
        context = {
        'online_count': online_count,
        'chat_group': self.chatroom
        }
        html = render_to_string("partials/online_count.html", context)

     # Send the rendered HTML as a WebSocket message
        await self.send(text_data=html)

