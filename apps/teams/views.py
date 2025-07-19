from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Team, TeamMember, User
from .forms import TeamCreationForm, OwnershipTransferForm, TeamEditForm
from django.contrib import messages
from .utils import switch_team, get_user_teams, get_current_team

@login_required
@require_POST
def switch_team_view(request):
    """
    Switch the current team context for the user.
    """
    team_id = request.POST.get('team_id')
    path = request.POST.get('next', 'dashboard:index')
    if not team_id:
        messages.error(request, "Invalid team selection.")
        return redirect(path)
    switch_team(request, team_id)
    return redirect(path)

@login_required
def team_index(request):
    """
    Render the team index page for the authenticated user.
    Lists all teams the user is a member of.
    """
    return redirect('teams:list')

@login_required
def team_create(request):
    """
    Render the team creation page.
    """
    form = TeamCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        team = form.save(commit=False)
        team.owner = request.user
        team.save()
        TeamMember.objects.create(user=request.user, team=team, role='admin')
        request.session['current_team_id'] = team.id
        messages.success(request, "Team created successfully!")
        return redirect('dashboard:index')
    return render(request, 'teams/create.html', {'form': form})

@login_required
def team_list(request):
    """
    List all teams the user is a member of.
    """
    teams = get_user_teams(request)
    if not teams:
        messages.info(request, "You are not a member of any teams.")
        return redirect('teams:create')
    current_team = get_current_team(request)
    return render(request, 'teams/list.html', {'teams': teams, 'current_team': current_team})


@login_required
def team_detail(request, slug):
    """
    View details of a specific team.
    """
    team = get_object_or_404(Team, slug=slug, members=request.user)
    return render(request, 'teams/detail.html', {'team': team})

@login_required
def team_transfer_ownership(request, slug):
    """
    Transfer ownership of a team to another user.
    """
    team = get_object_or_404(Team, slug=slug, owner=request.user)
    form = OwnershipTransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        new_owner_username = form.cleaned_data.get('new_owner')
        try:
            new_owner = User.objects.get(username=new_owner_username)
            team.transfer_ownership(new_owner)
            messages.success(request, "Ownership transferred successfully!")
            return redirect('teams:detail', slug=team.slug)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
    return render(request, 'teams/transfer.html', {'form': form, 'team': team})

@login_required
def leave_team(request, slug):
    """
    Allow a user to leave a team.
    """
    team = get_object_or_404(Team, slug=slug, members=request.user)
    if request.method == "POST":
        TeamMember.objects.filter(user=request.user, team=team).delete()
        messages.success(request, "You have left the team.")
        return redirect('teams:list')
    return render(request, 'teams/leave.html', {'team': team})


@login_required
def team_edit(request, slug):
    """
    Edit the details of a team.
    """
    team = get_object_or_404(Team, slug=slug, owner=request.user)
    form = TeamEditForm(instance=team, data=request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Team details updated successfully!")
        return redirect('teams:detail', slug=team.slug)
    return render(request, 'teams/edit.html', {'form': form, 'team': team})