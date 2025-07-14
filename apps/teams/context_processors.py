from .models import Team, TeamMember

def team_context_processor(request):
    """
    Context processor to add the current team and its members to the request context.
    """
    current_team_id = request.session.get('current_team_id')
    current_team = None
    team_members = []

    if current_team_id:
        try:
            current_team = Team.objects.get(id=current_team_id, members__user=request.user)
            team_members = current_team.members.all()
        except Team.DoesNotExist:
            pass

    return {
        'current_team': current_team,
        'team_members': team_members,
    }