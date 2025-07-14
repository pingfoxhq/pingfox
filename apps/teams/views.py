from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Team, TeamMember
from .forms import TeamCreationForm
from django.contrib import messages

@login_required
@require_POST
def switch_team(request):
    """
    Switch the current team context for the user.
    """
    team_id = request.POST.get('team_id')
    if not team_id:
        return redirect('dashboard:index')
    team = get_object_or_404(Team, id=team_id, members__user=request.user)
    request.session['current_team_id'] = team.id
    return redirect('dashboard:index')


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