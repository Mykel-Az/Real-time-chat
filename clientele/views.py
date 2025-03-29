from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404


# Create your views here.

@login_required
def home(request):
    users = User.objects.all()
    # profile = UserProfile.objects.all()
    return render(request, 'home.html', { 'users': users})


class SignUpView(generic.CreateView):
    form_class = ClienteleUserCreationForm
    template_name = 'account/sigup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
    


# class ChangePasswordView(PasswordChangeView):
#     form_class = PasswordChangeForm
#     template_name = 'account/password_change.html'
#     success_url = reverse_lazy('password_change_done')


# update Account info
class UserChange(generic.UpdateView):
    form_class = AccountsForm
    template_name = 'cliente/edit_user_account.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user


class CreateProfile(generic.CreateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = 'cliente/profile_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        redirect(self.success_url)
        return super().form_valid(form)


def edit_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            info = form.save(commit=False)

            if info.user == request.user:
                info.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('profile_detail', pk=profile.pk)  # Update to the correct redirect URL
            else:
                messages.error(request, 'You are not authorized to edit this profile.')
                return redirect('home')  # Redirect unauthorized users
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'cliente/profile_form.html', {'profile': profile, 'form': form})


def user_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    all_followers = profile.followers_no()
    all_following = profile.following_no()
    follows = profile.followers.filter(id=request.user.userprofile.id).exists()

    if request.method == "GET":
        user = profile.user
        full_name = f"{user.first_name} {user.last_name}"
        if user.is_active:
            profile.status == "Online"
        else:
            profile.status == 'Away'
    else:
        messages.error(request, "This user does not have a profile yet")
        return HttpResponseRedirect('/home')
   
    return render(request, 'cliente/profile.html', {'profile': profile, 'full_name': full_name, 'followers':all_followers, 'following':all_following, 'follows':follows})


def follow(request, pk):
    user_p = get_object_or_404(UserProfile, pk=request.user.userprofile.id)
    profile = get_object_or_404(UserProfile, pk=pk)
    # print(f'userp:{user_p}, pro:{profile}')
    if request.method == 'POST':
        if profile.followers.filter(id = request.user.userprofile.id).exists():
            profile.followers.remove(request.user)
            user_p.following.remove(profile.user)
        else:
            profile.followers.add(request.user)
            user_p.following.add(profile.user)
    return HttpResponseRedirect(reverse('user_profile', args=[str(pk)]))


def familiars(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    all_following = profile.following.all()
    all_followers = profile.followers.all()

    if request.GET.get("view")=='followings':
        users = all_following
    elif request.GET.get(('view'))=='followers':
        users = all_followers
    else:
        raise Http404

    return render(request, 'Cliente/familiars.html', {'users': users})