from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User

# Create your views here.

@login_required
def home_view(request):
    users = User.objects.all()
    return render(request, 'home.html',{'users': users})


def chathome(request, chatroom):
    pass


def room(request, room_name):
    return render(request, 'chat_room.html', {'room_name': room_name})