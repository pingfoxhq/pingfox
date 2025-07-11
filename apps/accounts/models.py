from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import secrets
from django.utils import timezone
from django_resized import ResizedImageField



def generate_api_key(length=40):
    """
    Generates a secure, URL-safe API key.

    - Uses `secrets` for cryptographic randomness.
    - Default length is 40 characters (plenty secure for public keys).
    - Characters are URL-safe (won't break in query strings or headers).
    """
    return secrets.token_urlsafe(length)[:length]


class User(AbstractUser):
    api_key = models.CharField(
        max_length=40,
        unique=True,
        default=generate_api_key,
        verbose_name=_("API Key"),
        help_text=_(
            "A unique API key for the user, used for authentication in API requests."
        ),
    )
    # Get gravatar from email in the default
    avatar = ResizedImageField(
        upload_to="avatars/",
        size=[200, 200],
        crop=["middle", "center"],
        quality=90,
        blank=True,
        verbose_name=_("Avatar"),
        help_text=_("User's profile picture, resized to 200x200 pixels."),
        default="defaults/avatar.png",
    )
    plan = models.ForeignKey(
        "billing.Plan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name=_("Billing Plan"),
        help_text=_("The billing plan associated with the user."),
    )
    plan_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Plan Expiry Date"),
        default=None,
        help_text=_("The date and time when the user's plan expires."),
    )
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Referral Code"),
        help_text=_("A unique referral code for the user, used for referrals."),
    )
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Referred By"),
        related_name="referrals",
        help_text=_("The user who referred this user, if any."),
    )

    accepted_terms = models.BooleanField(
        default=False,
        verbose_name=_("Accepted Terms"),
        help_text=_("Indicates whether the user has accepted the terms of service."),
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            base = self.username[:5] or "user"
            self.referral_code = f"{base}{secrets.token_hex(3)}"
        if not self.api_key:
            self.api_key = generate_api_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def is_pro(self):
        """
        Check if the user has a Pro plan.
        """
        return self.plan and self.plan.is_pro

    def has_active_plan(self):
        if not self.plan:
            return False
        if not self.plan_expires_at:
            return True  # Likely a free plan
        return self.plan_expires_at > timezone.now()
