from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import *
from .forms import *

# Create your views here.

@login_required
def home_view(request):
    users = User.objects.all()
    return render(request, 'home.html',{'users': users})


def chathome(request, chatroom_name='general-chat'):
    chat_group = get_object_or_404(GroupChatRoom, room_name=chatroom_name)
    chat_message = chat_group.group_messages.all()[:30]
    form = ChatMessageCreateForm()

    # for privatechats
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

        # for group chats
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)    

    # sending all messages to the template
    if request.method == 'POST':
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.room = chat_group
            context = {
                'message': message,
                'user': request.user
            }
        return render(request, 'chat/partials/chat_message_p.html', context)
    
    contexts = {
        'chat_messages': chat_message,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group
    }

    return render(request, 'chat/chat_room.html', contexts)

# def room(request, room_name):
#     return render(request, 'chat_room.html', {'room_name': room_name})