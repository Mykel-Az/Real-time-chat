# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from clientele.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Check if the UserProfile exists
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        # Create a new UserProfile if it doesn't exist
        UserProfile.objects.create(user=instance)