from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def login_view(request):
    """
    Render the login page.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard:dashboard")

    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    return redirect("home")

def register_view(request):
    """
    Render the registration page.
    """
    form = CustomUserCreationForm(request.POST or None)
    
    return render(request, "accounts/register.html", {"form": form})
