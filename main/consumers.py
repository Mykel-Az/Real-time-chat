import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import GroupChatRoom, GroupMessage
from clientele.models import UserProfile

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
        message_type = text_data_json.get('type')  # Get the message type

        if message_type == 'mark_as_read':
            # Handle marking a message as read
            message_id = text_data_json.get('message_id')
            print(f'message_id being presently marked: {message_id}')
            if message_id:
                message = await sync_to_async(GroupMessage.objects.get)(id=message_id)
                await sync_to_async(message.mark_as_read)(self.user)
                print(f'{message_id} as been read by {self.user.username}')

                # Notify the group that the message has been read
                await self.channel_layer.group_send(
                    self.room_code,
                    {
                        'type': 'message_read',
                        'message_id': message.id,
                        'read_by': self.user.username,
                    }
                )

        else:
            # Handle sending a new message
            text = text_data_json.get('message', '').strip()
            if text:  # Validate message
                # Create a GroupMessage
                message = await sync_to_async(GroupMessage.objects.create)(
                    content=text,
                    sender=self.user,
                    room=self.chatroom,
                    message_type=message_type  # Set the message type
                )

                # Update last_activity in the chatroom
                await sync_to_async(self.chatroom.save)()

                display_picture = await sync_to_async(self.get_user_profile_display_picture)(self.user)

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_code,
                    {
                        'type': 'chat_message',
                        'message': message.content,
                        'sender': self.user.username,
                        'timestamp': message.timestamp.isoformat(),
                        'display_picture': display_picture,
                        'message_type': message.message_type,  # Include message type
                        'is_seen': await sync_to_async(message.is_seen)()  # Include seen status
                    }
                )

    async def chat_message(self, event):
        message = event['message']
        sender = event.get('sender', 'Anonymous')
        display_picture = event['display_picture']
        is_seen = event.get('is_seen', False)

        message_obj = {
            'content': message,
            'sender': {
                'username': sender,
                'id': self.user.id if sender == self.user.username else None,
                'display_picture': display_picture
            },
            'timestamp': timezone.now(),
            'is_seen': is_seen
        }

        # Render the HTML for the new message
        html = await sync_to_async(render_to_string)(
            'chat/partials/chat_message_p.html',
            {'message': message_obj, 'request': {'user': self.user}, 'is_sender': sender == self.user.username}
        )

        # Send the rendered HTML to the client
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'html': html
        }))

    async def message_read(self, event):
        # Handle read receipt updates
        message_id = event['message_id']
        read_by = event['read_by']
        print(event)

        # Fetch the message
        message = await sync_to_async(GroupMessage.objects.get)(id=message_id)



        # Send the updated read status to the client
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': message_id,
            'read_by': read_by,
            'is_seen': await sync_to_async(message.is_seen)()
        }))

    def get_user_profile_display_picture(self, user):
        try:
            profile = user.userprofile
            return profile.display_picture.url if profile.display_picture else None
        except UserProfile.DoesNotExist:
            return None

    async def update_online_count(self):
        online_count = await sync_to_async(self.chatroom.users_online.count)()

        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        await self.channel_layer.group_send(self.room_code, event)

    async def online_count_handler(self, event):
        online_count = event['online_count']
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
                    'timestamp': message.timestamp.isoformat(),
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