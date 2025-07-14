# Send user activation email after registration
from django.core.mail import send_mail
import dramatiq
from apps.core.utils import get_or_null

from .models import UserActivation, User
from django.conf import settings


@dramatiq.actor
def send_user_activation_email(user_id):
    """
    Send an activation email to the user after registration.
    """
    user = get_or_null(User, id=user_id)
    if user:
        activation = UserActivation.objects.get(user=user)
        send_mail(
            subject="Activate your account, PingFox",
            message=f"Please activate your account using this code: {activation.activation_code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
        if settings.DEBUG:
            print(f"Activation email sent to {user.email} with code {activation.activation_code}")
        return True
    return False
