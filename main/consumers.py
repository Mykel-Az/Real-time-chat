import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import GroupChatRoom, GroupMessage, PrivateChatRoom, PrivateMessages


class GroupChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_code = self.scope['url_route']['kwargs']['room_code']

        # Use sync_to_async to call get_object_or_404
        self.chatroom = await sync_to_async(get_object_or_404)(GroupChatRoom, room_code=self.room_code)

        # Join room group
        await self.channel_layer.group_add(
            self.room_code,
            self.channel_name
        )

        # Add user to users_online
        if self.user not in await sync_to_async(list)(self.chatroom.users_online.all()):
            await sync_to_async(self.chatroom.users_online.add)(self.user)
            await self.update_online_count()

        # Update last_activity
        await sync_to_async(self.chatroom.save)()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_code,
            self.channel_name
        )

        # Remove user from online_user
        if self.user in await sync_to_async(list)(self.chatroom.users_online.all()):
            await sync_to_async(self.chatroom.users_online.remove)(self.user)
            await self.update_online_count()

        # Update last_activity
        await sync_to_async(self.chatroom.save)()


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json.get('message', '').strip()
        message_type = text_data_json.get('message_type', 'text')  # Default to 'text'
        mark_as_read = text_data_json.get('mark_as_read', False) # chek if message should be marked as read

        if text:  # Validate message
            # Create a GroupMessage
            message = await sync_to_async(GroupMessage.objects.create)(
                content=text,
                sender=self.user,
                room=self.chatroom,
                message_type=message_type  # Set the message type
            )

            # Mark message as read
            if mark_as_read:
                await sync_to_async(message.mark_as_read)(self.user)

            # Update last_activity in the chatroom
            await sync_to_async(self.chatroom.save)()

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': self.user.username,
                    'timestamp': message.timestamp.isoformat(),
                    'message_type': message.message_type, # Include message type
                    'is_read': mark_as_read # Include read status
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event.get('sender', 'Anonymous')

        message_obj = {
        'content': message,
        'sender': {'username': sender,
                   'id': self.user.id if sender == self.user.username else None},
        'timestamp': timezone.now()
        }

        html = await sync_to_async(render_to_string)(
        'chat/partials/chat_message_p.html',
        {'message': message_obj, 'request': {'user': self.user}, 'is_sender': sender == self.user}
        )

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'html': html
        }))

    async def update_online_count(self):
        online_count = await sync_to_async(self.chatroom.users_online.count)()

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        await self.channel_layer.group_send(self.room_code, event)

    async def online_count_handler(self, event):
        online_count = event['online_count']
        # context = {
        #     'online_count': online_count,
        #     'chat_group': self.chatroom
        # }
        # print(online_count)
        # html = await sync_to_async(render_to_string)("chat/chat_room.html", context)

        # Send the rendered HTML as a WebSocket message
        await self.send(text_data=json.dumps({
            'type': 'online_count',
            'online_count': online_count
        }))



class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_code = self.scope['url_route']['kwargs']['room_code']

        # Use sync_to_async to call get_object_or_404
        self.chatroom = await sync_to_async(get_object_or_404)(PrivateChatRoom, room_code=self.room_code)

        # Join room group
        await self.channel_layer.group_add(
            self.room_code,
            self.channel_name
        )

        # Add user to users_online
        if self.user not in await sync_to_async(list)(self.chatroom.user_online.all()):
            await sync_to_async(self.chatroom.user_online.add)(self.user)
            await self.update_online_count()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_code,
            self.channel_name
        )

        # Remove user from online_user
        if self.user in await sync_to_async(list)(self.chatroom.user_online.all()):
            await sync_to_async(self.chatroom.user_online.remove)(self.user)
            await self.update_online_count()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json.get('message', '').strip()

        if text:  # Validate message
            # create a GroupMessage
            message = await sync_to_async(PrivateMessages.objects.create)(
                content=text,
                sender=self.user,
                room=self.chatroom
            )

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': self.user.username,  # Include sender info
                    'timestamp': message.timestamp.isoformat()
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event.get('sender', 'Anonymous')

        message_obj = {
        'content': message,
        'sender': {'username': sender,
                   'id': self.user.id if sender == self.user.username else None
                   },
        'timestamp': timezone.now()
        }

        html = await sync_to_async(render_to_string)(
        'chat/partials/chat_message_p.html',
        {'message': message_obj, 'request': {'user': self.user}, 'is_sender': sender == self.user.username}
        )

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'html': html
        }))

    async def update_online_count(self):
        online_count = await sync_to_async(self.chatroom.user_online.count)()

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        await self.channel_layer.group_send(self.room_code, event)

    async def online_count_handler(self, event):
        online_count = event['online_count']

        # Send the rendered HTML as a WebSocket message
        await self.send(text_data=json.dumps({
            'type': 'online_count',
            'online_count': online_count
        }))