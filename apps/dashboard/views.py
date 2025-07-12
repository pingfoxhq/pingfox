from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    """
    Render the dashboard page for authenticated users.
    """
    return render(request, "dashboard/dashboard.html")