from django.core.exceptions import PermissionDenied
from functools import wraps
from apps.teams.models import Team
from apps.core.utils import get_or_null

def plan_required(feature_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            team_id = getattr(request.session, "current_team_id", None)
            team = get_or_null(Team, id=team_id, members__in=[request.user])
            if not team:
                raise PermissionDenied("No active team selected.")

            if not team.plan or feature_name not in team.plan.features:
                raise PermissionDenied("Your plan does not include access to this feature.")
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
                if not isinstance(current_value, (int, float)) or current_value < min_value:
                    raise PermissionDenied(f"'{feature_name}' limit too low for this action.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def enforce_team_resource_limit(resource_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            team = get_or_null(Team, id=request.session.get("current_team_id"), members__in=[request.user])
            if team.is_limit_exceeded(resource_name):
                raise PermissionDenied(f"{resource_name.capitalize()} limit reached.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
