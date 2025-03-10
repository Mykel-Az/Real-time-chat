from django.db import models
from clientele.models import User, UserProfile
import shortuuid

# Create your models here.

class GroupChatRoom(models.Model):
    room_code = models.CharField(max_length=25, unique=True, default=shortuuid.uuid)
    groupchat_name = models.CharField(max_length=50, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchat_admin', on_delete=models.CASCADE, blank=True)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='groupchat_members', blank=True)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.room_code}: {self.groupchat_name}'


class PrivateChatRoom(models.Model):
    room_code = models.CharField(max_length=15, unique=True, default=shortuuid.uuid)
    members = models.ManyToManyField(User, related_name='privatechat_members', blank=True)
    user_online = models.ManyToManyField(User, related_name='user_online', blank=True)

    def __str__(self):
        return f'Private Chat: {self.room_code}: {self.members.all()}'
    

class GroupMessage(models.Model):

    MESSAGE_TYPES = (
        ('text', 'Text Message'),
        ('file', 'File Upload'),
        ('system', 'System Message'),
    )

    room = models.ForeignKey(GroupChatRoom, related_name='group_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    message_type = models.CharField(max_length=15, choices=MESSAGE_TYPES, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='receipts')
    edited_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender}: {self.content}'
    
    def mark_as_read(self, user):
        if user not in self.read_by.all():
            self.read_by.add(user)

    def mark_as_edited(self):
        from django.utils import timezone
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()


class PrivateMessages(models.Model):
    room = models.ForeignKey(PrivateChatRoom, related_name='private_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender}: {self.content}'