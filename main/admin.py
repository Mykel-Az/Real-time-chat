from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(GroupChatRoom)
admin.site.register(GroupMessage)
admin.site.register(PrivateChatRoom)
admin.site.register(PrivateMessages)