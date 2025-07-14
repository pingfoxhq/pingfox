from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_index(request):
    """
    Render the dashboard page for authenticated users.
    """

    teams = request.user.team_members.all() if request.user.is_authenticated else []
    sites = request.user.sites.all() if request.user.is_authenticated else []

    if not teams:
        return redirect('teams:create')
    context = {
        'sites': sites,
    }
    return render(request, "dashboard/index.html", context=context)