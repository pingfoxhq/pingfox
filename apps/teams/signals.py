from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from apps.billing.models import Plan
from .models import Team
from django.db.models.signals import post_save


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


@receiver(post_save, sender=Team)
def set_base_free_plan(sender, instance, created, **kwargs):
    """
    Set the base free plan for a team when it is created.
    This assumes that the Plan model has a 'base_free' field.
    """
    if created:
        # Assuming you have a method to get the base free plan
        base_free_plan = Plan.objects.get(base_free=True)
        instance.plan = base_free_plan
        instance.save()
