from django.shortcuts import render, get_object_or_404
from apps.sites.models import Site
from django.contrib.auth.decorators import login_required
from .services import get_site_analytics
import csv
from .models import PageView, VisitorSession
from django.http import HttpResponse
from django.db.models import F


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


@login_required
def site_chart(request, site_id):
    """
    Render the analytics chart for a specific site.
    """
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)
    daily = get_site_analytics(site, "daily")
    hourly = get_site_analytics(site, "hourly")
    minute = get_site_analytics(site, "minute")
    return render(
        request,
        "analytics/partials/site_chart.html",
        {
            "daily": daily,
            "hourly": hourly,
            "minute": minute,
        },
    )


@login_required
def download_csv(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)
    # Add the VisitorSession connected to the page views
    VisitorSession.objects.filter(page_views__site=site).distinct()
    page_views = (
        PageView.objects.filter(site=site)
        .order_by("-timestamp")
        .annotate(
            visitor_pf_id=F("visitor__pf_id"),
            user_agent=F("visitor__user_agent"),
        )
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{site.site_id}_pageviews.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Timestamp", "URL", "Referrer", "User Agent", "Visitor PF ID"])

    for view in page_views:
        writer.writerow([view.timestamp, view.url, view.referrer, view.user_agent, view.visitor_pf_id])

    return response


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
