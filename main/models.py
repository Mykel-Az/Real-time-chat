from django.db import models
from django.contrib.auth.models import User
import shortuuid

# Create your models here.

class GroupChatRoom(models.Model):
    room_code = models.CharField(max_length=15, unique=True, default=shortuuid.uuid)
    groupchat_name = models.CharField(max_length=50, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchat_admin', on_delete=models.CASCADE, blank=True)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='groupchat_members', blank=True)

    def __str__(self):
        return f'{self.room_code}: {self.groupchat_name}'


# class PrivateChatRoom(models.Model):
#     room_code = models.CharField(max_length=15, unique=True, default=shortuuid.uuid)
#     members = models.ManyToManyField(User, related_name='privatechat_members', blank=True)

#     def __str__(self):
#         return f'Private Chat: {self.room_code}'
    

class GroupMessage(models.Model):
    room = models.ForeignKey(GroupChatRoom, related_name='group_messages', on_delete=models.CASCADE)   
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender}: {self.content}'


# class PrivateMessage(models.Model):
#     room = models.ForeignKey(PrivateChatRoom, related_name='private_messages', on_delete=models.CASCADE)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['timestamp']

#     def __str__(self):
#         return f'{self.sender}: {self.content}'