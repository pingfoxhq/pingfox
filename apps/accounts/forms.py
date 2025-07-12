from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from apps.forms.forms import TailwindFormMixin

class CustomUserCreationForm(TailwindFormMixin, UserCreationForm):
    """
    Custom form for user registration with tailwind styling
    """
    pass

class CustomAuthenticationForm(TailwindFormMixin, AuthenticationForm):
    """
    Custom form for user login with tailwind styling
    """
    pass