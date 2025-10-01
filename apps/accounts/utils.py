from .models import Team
from apps.core.utils import get_or_null
from django.shortcuts import redirect

def switch_team(request, team_id):
    """
    Switch the current team context for the user.
    """
    team = get_or_null(Team, id=team_id, members__in=[request.user])
    request.session['current_team_id'] = team.id


def get_current_team(request):
    """
    Get the current team context for the user.
    """
    team_id = request.session.get('current_team_id')
    if team_id:
        return get_or_null(Team, id=team_id, members__in=[request.user])
    else:
        team  = get_user_teams(request).first()
        if team:
            request.session['current_team_id'] = team.id
            return team
        return redirect('accounts:teams_create')


def get_user_teams(request):
    """
    Get all teams associated with the user.
    """
    return request.user.teams.all() if request.user.is_authenticated else None