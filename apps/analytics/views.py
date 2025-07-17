from django.shortcuts import render, get_object_or_404
from apps.sites.models import Site
from django.contrib.auth.decorators import login_required



@login_required
def analytics_index(request):
    """
    Render the analytics index for the authenticated user.
    """
    # Fetch data for the dashboard, e.g., site statistics, visitor counts, etc.
    # This is a placeholder; actual data fetching logic will depend on your models and requirements.

    context = {
        "active_tab": "analytics",
        # Add other context variables as needed
    }

    return render(request, "analytics/index.html", context)


def serve_pf_js(request):
    """
    Serve the PingFox tracking script.
    """
    site_url = request.build_absolute_uri("/")
    response = render(
        request,
        "analytics/pf.js",
        content_type="application/javascript",
        context={"site_url": site_url},
    )
    response["Cache-Control"] = "no-cache"
    return response
