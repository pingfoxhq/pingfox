from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from apps.accounts.forms import (
    CustomAuthenticationForm,
    UserEditForm,
    UserProfileEditForm,
    UserSignupForm,
    UserActivationForm,
    UserActivationEmailChangeForm,
)
from apps.core.utils import get_or_null
from .models import UserActivation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .tasks import send_user_activation_email


@login_required
def accounts_dashboard(request):
    """
    Render the user profile page for the authenticated user.
    Allows the user to edit their profile and user information.
    """
    uform = UserEditForm(request.POST or None or None, instance=request.user)
    pform = UserProfileEditForm(
        request.POST or None, request.FILES or None, instance=request.user.userprofile
    )

    if request.method == "POST" and uform.is_valid() and pform.is_valid():
        uform.save()
        pform.save()
        messages.success(request, "Userprofile updated successfully.")
        return redirect("accounts:index")

    return render(request, "accounts/index.html", {"uform": uform, "pform": pform})


def login_view(request):
    """
    Render the login page.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("sites:index")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    return redirect("home")


def register_view(request):
    """
    Render the first step of the user registration wizard.
    And send the activation email.
    """
    form = UserSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        login(request, user)
        messages.success(
            request,
            "Registration successful! Please check your email for activation code.",
        )
        return redirect("accounts:activate")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def activate_view(request):
    """
    Render the second step of the user registration wizard.
    Handle user activation.
    """
    form = UserActivationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        activation_code = form.cleaned_data.get("activation_code")
        activation = get_or_null(
            UserActivation,
            user=request.user,
            activation_code=activation_code,
            is_active=False,
        )
        if activation:
            if activation.activate():
                messages.success(
                    request,
                    "Your account has been activated successfully!",
                )
                login(request, activation.user)
            else:
                messages.error(request, "Activation code is invalid or expired.")
            return redirect("dashboard:index")
        else:
            messages.error(request, "Invalid activation code.")

    return render(request, "accounts/activate.html", {"form": form})


@login_required
def resend_activation_view(request):
    """
    Resend the activation email to the user.
    Also get the email from the user, if they want to change it.
    """
    form = UserActivationEmailChangeForm(
        request.POST or None, initial={"email": request.user.email}
    )
    if form.is_valid() and request.method == "POST":
        email = form.cleaned_data.get("email")
        if email:
            request.user.email = email
            request.user.save()
        send_user_activation_email.send(request.user.id)
        messages.success(
            request, "Activation email resent successfully! Please check your inbox."
        )
        return redirect("accounts:activate")
    return render(request, "accounts/resend_activation.html", {"form": form})
