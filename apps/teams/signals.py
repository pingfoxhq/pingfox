from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Team, User


@receiver(user_logged_in)
def set_current_team_id(sender, request, user, **kwargs):
    """
    Set the current team ID in the session when a user logs in.
    This assumes that the user has a default team set.
    """
    try:
        default_team = request.user.teams.first()  # Assuming the user has a method to get their default team
        if default_team:
            request.session['current_team_id'] = default_team.id
        else:
            request.session.pop('current_team_id', None)
    except Team.DoesNotExist:
        request.session.pop('current_team_id', None)