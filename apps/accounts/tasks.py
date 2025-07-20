import dramatiq
from django.conf import settings
from django.core.mail import send_mail
from apps.core.utils import get_or_null
from apps.accounts.models import UserActivation, User


@dramatiq.actor
def send_user_activation_email(user_id):
    """
    Send an activation email to the user with the activation code.

    Args:
        user_id (int): The ID of the user to send the activation email to.
    """
    user = get_or_null(User, id=user_id)
    if not user:
        print(f"User with id {user_id} not found.")
        return

    activation = get_or_null(UserActivation, user=user)
    if not activation:
        activation = UserActivation.objects.create(user=user)

    activation.regenerate_activation_code()  # Ensure this saves

    try:
        send_mail(
            subject="Activate your account, PingFox",
            message=f"Please activate your account using this code: {activation.activation_code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        print(
            f"✅ Activation email sent to {user.email} with code {activation.activation_code}"
        )
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
