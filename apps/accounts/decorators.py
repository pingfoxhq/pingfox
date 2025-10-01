from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from django.http import HttpRequest
from .models import Team, UserActivation
from .utils import get_or_null, get_user_teams
from django.contrib import messages


def require_team(view_func):
    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):

        if UserActivation.objects.filter(user=request.user, is_active=False).exists():
            messages.error(
                request, "Please activate your account to access this feature."
            )
            return redirect("accounts:activation_required")

        team_id = request.session.get("current_team_id")

        # Check session first
        if team_id:
            team = get_or_null(Team, id=team_id, members__in=[request.user])
            if team:
                request.team = team
                return view_func(request, *args, **kwargs)

        # If not in session, get the first team
        user_teams = get_user_teams(request)
        team = user_teams.first()

        if team:
            request.session["current_team_id"] = team.id
            request.team = team
            return view_func(request, *args, **kwargs)

        # No team — redirect to team creation page
        messages.error(request, "You need to create a team first.")
        return redirect("accounts:teams_create")

    return _wrapped_view


def plan_required(feature_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            team_id = getattr(request.session, "current_team_id", None)
            team = get_or_null(Team, id=team_id, members__in=[request.user])
            if not team:
                raise PermissionDenied("No active team selected.")

            if not team.plan or feature_name not in team.plan.features:
                raise PermissionDenied(
                    "Your plan does not include access to this feature."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def require_feature(feature_name, min_value=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            team_id = getattr(request.session, "current_team_id", None)
            team = get_or_null(Team, id=team_id, members__in=[request.user])
            if not team or not hasattr(team, "plan") or not team.plan:
                raise PermissionDenied("No active team or plan assigned.")

            features = team.plan.features or {}

            # Feature not found in plan
            if feature_name not in features:
                raise PermissionDenied(f"Your plan does not support '{feature_name}'.")

            # If min_value specified, check for numeric threshold
            if min_value is not None:
                current_value = features.get(feature_name)
                if (
                    not isinstance(current_value, (int, float))
                    or current_value < min_value
                ):
                    raise PermissionDenied(
                        f"'{feature_name}' limit too low for this action."
                    )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def enforce_team_resource_limit(resource_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            team = get_or_null(
                Team,
                id=request.session.get("current_team_id"),
                members__in=[request.user],
            )
            if not team:
                messages.error(
                    request, "No active team selected."
                )
                return redirect("accounts:teams_create")
            if team.is_limit_exceeded(resource_name):
                messages.error(
                    request, f"{resource_name.capitalize()} limit reached."
                )
                return redirect(f"accounts:teams_over_limit")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
