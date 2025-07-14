from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, UserProfile, UserActivation

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile instance whenever a User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)
        UserActivation.objects.create(user=instance)