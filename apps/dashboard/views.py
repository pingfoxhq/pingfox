from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.teams.utils import get_current_team
from django.contrib import messages


@login_required
def dashboard_index(request):
    """
    Render the dashboard page for authenticated users.
    """
    print(get_current_team(request))
    if get_current_team(request) is None:
        messages.info(request, "Please create a team to get started.")
        return redirect('teams:create')
    return render(request, "dashboard/index.html")