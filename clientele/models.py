from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.urls import reverse

# Create your models here.

class UserProfile(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    ]
    
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    website = models.URLField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    display_picture = models.ImageField(upload_to='img/profile_pics/', blank=True, null=True, default='img/profile_pics/default_profile.jpg')
    status = models.CharField(max_length=10, default='offline')
    country = CountryField(blank_label="(select country)")
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, null=True,)
    dob = models.DateField(blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    # theme = models.CharField(max_length=10, blank=True, default='light')
    verified = models.BooleanField(default=False)

    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)

    def followers_no(self):
        return self.followers.count()
    
    def following_no(self):
        return self.following.count()

    def __str__(self):
        return str(self.user)
    
    def get_absolute_url(self):
        return reverse("user_profile", args=[str(self.id)])