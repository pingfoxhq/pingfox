from django.shortcuts import render, redirect
from django.contrib import messages
from apps.teams.utils import get_user_teams
def home(request):
    """
    Render the home page of the application.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'core/home.html')

def home_unauth(request):
    """
    Redirect to the home page.
    """
    return render(request, 'core/home.html')


def onboarding(request):
    """
    Render the onboarding page for new users.
    """
    if not len(get_user_teams(request)) > 0:
        messages.info(request, "Please create a team to get started.")
        return redirect('teams:create')

    return render(request, 'core/onboarding.html')