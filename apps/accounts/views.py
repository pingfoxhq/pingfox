from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from apps.accounts.forms import (
    CustomAuthenticationForm,
    UserEditForm,
    UserProfileEditForm,
    UserSignupForm,
    UserActivationForm,
)
from .models import User, UserActivation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .tasks import send_user_activation_email


@login_required
def index(request):
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
            return redirect("dashboard:index")

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
        user.is_active = False  # Deactivate account until it is activated
        user.save()
        request.session["activation_code"] = user.activation.activation_code
        request.session["user_id"] = user.id
        send_user_activation_email.send(user.id)
        messages.success(
            request,
            "Registration successful! Please check your email for activation code.",
        )
        return redirect("accounts:activate")
    return render(request, "accounts/register.html", {"form": form})


def activate_view(request):
    """
    Render the second step of the user registration wizard.
    Handle user activation.
    """
    form = UserActivationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        activation_code = form.cleaned_data.get("activation_code")
        user_id = request.session.get("user_id")
        activation = UserActivation.objects.filter(
            user__id=user_id, activation_code=activation_code
        ).first()
        if activation:
            activation.activate()
            messages.success(
                request,
                "Your account has been activated successfully!",
            )
            login(request, activation.user)
            return redirect("dashboard:index")
        else:
            messages.error(request, "Invalid activation code.")

    return render(request, "accounts/activate.html", {"form": form})
