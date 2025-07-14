from .models import Team, TeamMember
from apps.core.utils import get_or_null

def switch_team(request, team_id):
    """
    Switch the current team context for the user.
    """
    team = get_or_null(Team, id=team_id, members__in=[request.user])
    request.session['current_team_id'] = team.id