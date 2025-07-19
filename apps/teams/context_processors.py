from .utils import get_current_team, get_user_teams

def team_context_processor(request):
    """
    Context processor to add the current team and its members to the request context.
    """
    if not request.user.is_authenticated:
        return {}
    current_team = get_current_team(request)
    user_teams = get_user_teams(request)
    return {
        'current_team': current_team,
        'user_teams': user_teams,
    }