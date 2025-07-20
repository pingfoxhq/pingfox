from django.shortcuts import render, redirect
from django.contrib import messages
from apps.accounts.utils import get_user_teams
from django.http import HttpResponse
from django.conf import settings


def home(request):
    """
    Render the home page of the application.
    """
    if request.user.is_authenticated:
        return redirect("analytics:index")
    return render(request, "core/home.html")


def home_unauth(request):
    """
    Redirect to the home page.
    """
    return render(request, "core/home.html")


def onboarding(request):
    """
    Render the onboarding page for new users.
    """
    if not len(get_user_teams(request)) > 0:
        messages.info(request, "Please create a team to get started.")
        return redirect("teams:create")

    return render(request, "core/onboarding.html")


def verification_token(request):
    """
    Returns the current site verification token for the analytics site verification.
    """
    return HttpResponse(
        settings.PINGFOX_VERIFICATION_TOKEN,
    )
