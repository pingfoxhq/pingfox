from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User, UserProfile


class UserSignupForm(UserCreationForm):
    """
    Step 1 of the user registration wizard.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")


class UserActivationForm(forms.Form):
    """
    Form to handle user activation.
    """

    activation_code = forms.CharField(
        max_length=6,
        label="Activation Code",
        widget=forms.TextInput(attrs={"placeholder": "Enter your activation code"}),
    )


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom form for user login with tailwind styling
    """

    pass


class UserEditForm(forms.ModelForm):
    """
    Custom form for editing user profile with tailwind styling
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )


class UserProfileEditForm(forms.ModelForm):
    """
    Custom form for editing user profile with tailwind styling
    """

    class Meta:
        model = UserProfile
        fields = (
            "avatar",
        )

    widgets = {
        "avatar": forms.ClearableFileInput(attrs={"class": "file-input"}),
    }