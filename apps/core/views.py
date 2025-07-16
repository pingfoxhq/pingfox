from django.shortcuts import render, redirect
from django.contrib import messages
from apps.teams.utils import get_user_teams
from django.http import HttpResponse


def home(request):
    """
    Render the home page of the application.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:index")
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
        """
    _EHy9O66oPALqFa4FUBvEBIphxpvEx3UzAemUBfoV6jFTzQBQbRvEVLxlSpnkpEYZCdBstpjJppfnI7uVAewqQCbGnqARwU_dH-aQly0jShS9KEHKNnbGbXobWLLw7zmGt3EW3H7f3Rhnj7ispDgo52uJcsBROAJR9FfOf-3u0UwEmEH8a73Ddm3bwt-dogAqtdIYzI8aL12e1TxgrIVZ-F8kvT4rzeb371ESh-QKag2dy_5x6UINEpmlnDVw_QQak8Eh0WIR-Pkqp9EzpPF4P4wqvfB06e0kn9soijX4_115uLLh05dzOg99fBkpDF0VPhsYs88rIEhk6sFaHAScw
""".strip()
    )
