from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.views import generic
from .models import *
from .forms import *

# Create your views here.

@login_required
def chat_view(request):
    users = User.objects.all()
    privatechats = PrivateChatRoom.objects.filter(members = request.user).all()
    groupchats = GroupChatRoom.objects.all()
    return render(request, 'chat.html',{'privatechats': privatechats, 'groupchats': groupchats, 'users': users})


@login_required
def groupchat(request, room_code):
    chat_group = get_object_or_404(GroupChatRoom, room_code=room_code)  # Use room_code instead of groupchat_name
    chat_messages = chat_group.group_messages.all()[:30]
    form = ChatMessageCreateForm()

    # For private chats
    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    # For group chats
    if not chat_group.is_private and request.user not in chat_group.members.all():
        chat_group.members.add(request.user)

    # Handle form submission
    if request.method == 'POST':
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.room = chat_group
            message.save()
            return JsonResponse({'status': 'success'})  # Provide feedback

    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'room_code': room_code,
        'chat_group': chat_group
    }

    return render(request, 'chat/chat_room.html', context)



def creategroupchat(request):
    form = NewGroupchatCreateForm()
    if request.method == 'POST':
        form = NewGroupchatCreateForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            # groupusers = request.POST.get('members')
            # groupusers = form.members.value
            # new_groupchat.members = 
            # print(groupusers)

            groupusers = form.cleaned_data['members']
            new_groupchat.members.add(*groupusers)
            new_groupchat.members.add(request.user)
            print(groupusers)
            return redirect('chat', new_groupchat.room_code)
        
    context = {
        'form': form
    }
    return render(request, 'chat/creategroupchat.html', context)
            

def privatechat(request, username):
    if request.user.username == username:
        return redirect('chat')
    
    other_user = get_object_or_404(User, username=username)
    chatroom = PrivateChatRoom.objects.filter(members = request.user).filter(members = other_user).distinct().first()

    if not chatroom:       
        chatroom = PrivateChatRoom.objects.create()
        print(chatroom.room_code)
        chatroom.members.add(request.user, other_user)

    return redirect('directchat', room_code=chatroom.room_code)


def directchat(request, room_code):
    chat_group = get_object_or_404(PrivateChatRoom, room_code=room_code)  # Use room_code instead of groupchat_name
    chat_messages = chat_group.private_messages.all()[:30]
    form = ChatMessageCreateForm()

    other_user = None
    for member in chat_group.members.all():
        if member != request.user:
            other_user = member
            break

    if not other_user:
        raise Http404("Other Users not found")

    if request.method == 'POST':
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.room = chat_group
            message.save()
            return JsonResponse({'status': 'success'})
        
    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'room_code': room_code,
        'chat_group': chat_group,
        'online_count': chat_group.user_online.count()
    }

    return render(request, 'chat/direct_chat.html', context)