from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from .forms import PingFoxFormCreatationForm
from django.contrib import messages
from apps.teams.models import Team

from apps.teams.utils import get_current_team

@login_required
def form_index(request):
    """
    Render the form index page for the authenticated user.
    """
    return redirect("forms:list")

@login_required
def form_list(request):
    """
    Render the list of forms for the authenticated user.
    """
    # Fetch forms created by the user or associated with their team
    team = get_current_team(request)
    forms = team.forms.all()
    return render(request, "forms/list.html", {"forms": forms, "team": team})

@login_required
def form_create(request):
    """
    Render the form creation page for the authenticated user.
    """
    # Get the currently selected team for the user session
    team = get_current_team(request)
    if team.is_limit_exceeded("forms"):
        messages.error(request, "You have reached the limit for creating forms in this team.")
        return redirect("forms:list")
    form = PingFoxFormCreatationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(commit=False)
        form.ownder = request.user

        messages.success(request, "Form created successfully.")
        return redirect("forms:builder", slug=form.slug)

    return render(request, "forms/create.html", {"form": form})


@login_required
def form_builder(request, slug):
    """
    Render the form builder page for the authenticated user.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug)
    if request.method == "POST":
        # Handle form submission logic here
        pass
    return render(request, "forms/builder.html")
