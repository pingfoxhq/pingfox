from django.db import models
import secrets
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

User = get_user_model()

def generate_secret_key(length=40):
    """
    Generates a secure, URL-safe secret key.

    - Uses `secrets` for cryptographic randomness.
    - Default length is 40 characters (sufficiently secure for secret keys).
    - Characters are URL-safe (won't break in query strings or headers).
    """
    return secrets.token_urlsafe(length)[:length]
