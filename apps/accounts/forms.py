from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User, UserProfile, Team


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
        fields = ("avatar",)

    widgets = {
        "avatar": forms.ClearableFileInput(attrs={"class": "file-input"}),
    }


class UserActivationEmailChangeForm(forms.Form):
    """
    Form to handle email change for user activation.
    """

    email = forms.EmailField(
        max_length=254,
        label="New Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your new email address"}),
        help_text="If you want to change your email address, please enter the new email here.",
    )


class TeamCreationForm(forms.ModelForm):
    """
    Form for creating a new team.
    """

    name = forms.CharField(
        max_length=100,
        help_text="Enter the name of your team.",
        widget=forms.TextInput(attrs={"placeholder": "Team Name"}),
    )

    class Meta:
        model = Team
        fields = [
            "name",
        ]


class OwnershipTransferForm(forms.ModelForm):
    """
    Form for transferring ownership of a team.
    """

    new_owner = forms.CharField(
        max_length=150,
        help_text="Enter the username of the new team owner.",
        widget=forms.TextInput(attrs={"placeholder": "New Owner Username"}),
    )

    class Meta:
        model = Team
        fields = [
            "new_owner",
        ]


class TeamEditForm(forms.ModelForm):
    """
    Form for editing team details.
    """

    class Meta:
        model = Team
        fields = [
            "name",
            "logo",
        ]


class TeamInviteForm(forms.ModelForm):
    """
    Form for inviting a user to a team.
    """

    email = forms.CharField(
        max_length=150,
        help_text="Enter the email of the user to invite.",
        widget=forms.TextInput(attrs={"placeholder": "User Email"}),
    )

    class Meta:
        model = Team
        fields = [
            "email",
        ]
