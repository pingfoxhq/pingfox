import logging
from django.shortcuts import redirect, resolve_url
from django.contrib import messages
from django.http import JsonResponse
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

from .models import UserActivation
from apps.core.utils import get_or_null, is_htmx  # assume you have `is_htmx`

logger = logging.getLogger(__name__)

EXTEMPT_URLS = [
    "accounts:login",
    "accounts:logout",
    "accounts:register",
    "accounts:resend_activation",
    "accounts:activate",
    "home",
    "onboarding",
    "verification_token",
    "home_unauth",
]


class UserActivationMiddleware(MiddlewareMixin):
    """
    Ensures authenticated users are activated.
    Handles HTML, HTMX, and JSON-aware requests gracefully.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.exempt_paths = set(resolve_url(name) for name in EXTEMPT_URLS)

    def process_request(self, request):
        user = request.user

        if request.path.startswith("/admin/"):
            return  # Skip admin paths

        if not user.is_authenticated:
            return  # unauthenticated, skip

        if request.path in self.exempt_paths:
            return  # exempt path

        activation_required = get_or_null(UserActivation, user=user, is_active=False)
        if not activation_required:
            return  # already activated

        # log the block
        logger.info(f"[UserActivationMiddleware] Blocking access to {request.path} for inactive user: {user.username}")

        # Handle HTMX requests
        if is_htmx(request):
            response = JsonResponse(
                {"redirect": resolve_url("accounts:activate")},
                status=278,  # HTMX special redirect code
            )
            response["HX-Redirect"] = resolve_url("accounts:activate")
            return response

        # Handle API/JSON requests
        if request.content_type == "application/json" or request.headers.get("Accept") == "application/json":
            return JsonResponse(
                {"detail": "Account not activated."},
                status=403
            )

        # Regular web request
        messages.info(request, "Please activate your account.")
        return redirect("accounts:activate")
