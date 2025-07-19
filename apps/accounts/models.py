from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import secrets
from django.utils import timezone
from django_resized import ResizedImageField

User = get_user_model()


def generate_api_key(length=40):
    """
    Generates a secure, URL-safe API key.

    - Uses `secrets` for cryptographic randomness.
    - Default length is 40 characters (plenty secure for public keys).
    - Characters are URL-safe (won't break in query strings or headers).
    """
    return secrets.token_urlsafe(length)[:length]


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile",
        verbose_name=_("User Profile"),
        help_text=_("The user associated with this profile."),
    )
    avatar = ResizedImageField(
        upload_to="uploads/avatars/",
        size=[200, 200],
        crop=["middle", "center"],
        quality=90,
        verbose_name=_("Avatar"),
        null=True,
        blank=True,
        help_text=_("User's profile picture, resized to 200x200 pixels."),
        default="defaults/avatar.png",
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        if not self.avatar or self.avatar.name.startswith("defaults/"):
            self.avatar = "defaults/avatar.png"
        super().save(*args, **kwargs)

    def teams(self):
        """
        Returns a list of teams the user is a member of.
        """
        return self.user.team_members.all()


def generate_activation_code():
    """
    Generates a secure random activation code.

    Returns:
        str: A secure random activation code.
    """
    while True:
        code = secrets.token_hex(3).upper()
        if not UserActivation.objects.filter(activation_code=code).exists():
            return code


def generate_activation_code_expiration():
    """
    Generates a default expiration date for activation codes.

    Returns:
        datetime: A datetime object set to 24 hours from now.
    """
    return timezone.now() + timezone.timedelta(days=1)


class UserActivation(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="activation",
        verbose_name=_("User Activation"),
        help_text=_("The user associated with this activation."),
    )
    activation_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_activation_code,
        verbose_name=_("Activation Code"),
        help_text=_("A unique code for activating the user's account."),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("Is Active"),
        help_text=_("Indicates whether the user's account is active."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the activation was created."),
    )
    expiration_date = models.DateTimeField(
        default=generate_activation_code_expiration,
        verbose_name=_("Expiration Date"),
        help_text=_("The date and time when the activation code expires."),
    )

    def __str__(self):
        return f"Activation for {self.user.username}"

    def is_expired(self):
        """
        Check if the activation code is expired.
        """
        return timezone.now() > self.expiration_date

    def activate(self):
        """
        Activate the user's account.
        """
        if not self.is_active and not self.is_expired():
            self.user.is_active = True
            self.user.save()
            self.is_active = True
            self.save()
            return True
        return False

    def regenerate_activation_code(self):
        """
        Regenerate the activation code.
        """
        self.activation_code = generate_activation_code()
        self.expiration_date = generate_activation_code_expiration()
        self.save()

    def save(self, *args, **kwargs):
        if not self.activation_code:
            self.activation_code = generate_activation_code()
        if not self.expiration_date:
            self.expiration_date = generate_activation_code_expiration()
        super().save(*args, **kwargs)
