from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.accounts.tasks import send_user_activation_email
from .models import User, UserProfile, UserActivation


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile instance whenever a User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)
        UserActivation.objects.create(user=instance)
        send_user_activation_email.send(instance.id)
