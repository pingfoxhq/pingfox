from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .services import get_site_analytics
from django.core.paginator import Paginator
from django.contrib import messages
import csv, json
from .models import PageView, VisitorSession, Site
from django.http import HttpResponse
from django.db.models import F
from apps.analytics.services import (
    get_site_analytics,
    get_visitors,
    get_page_views,
    get_top_pages,
    get_top_referrers,
    get_pageviews_by_day,
)
from apps.analytics.models import PageView
from apps.accounts.utils import get_current_team
from .forms import SiteCreationForm
from apps.analytics.tasks import verify_site


@login_required
def analytics_index(request):
    """
    Render the analytics index for the authenticated user.
    """
    # Fetch data for the dashboard, e.g., site statistics, visitor counts, etc.
    # This is a placeholder; actual data fetching logic will depend on your models and requirements.

    return render(request, "analytics/index.html")


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
        writer.writerow(
            [
                view.timestamp,
                view.url,
                view.referrer,
                view.user_agent,
                view.visitor_pf_id,
            ]
        )

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


@login_required
def index(request):
    """
    Render the analytics index page for the authenticated user.
    This page lists all sites created by the user and provides options to create, edit, or delete sites.
    """
    max_sites = get_current_team(request).feature_limit("sites_limit")
    sites = Site.objects.filter(team=get_current_team(request), form__isnull=True)
    can_create = not get_current_team(request).is_limit_exceeded("sites") if get_current_team(request) else True
    return render(
        request, "analytics/index.html", {"max_sites": max_sites, "sites": sites, "can_create": can_create}
    )


@login_required
def create_site(request):
    """
    Render the site creation form for the authenticated user.
    """
    team = get_current_team(request)
    if team.is_limit_exceeded("sites"):
        messages.error(
            request,
            "You have reached the maximum number of sites allowed for your team.",
        )
        return redirect("analytics:index")

    form = SiteCreationForm(request.POST or None, initial={"user": request.user})
    if request.method == "POST" and form.is_valid():
        site: Site = form.save(commit=False)
        site.owner = request.user
        site.team = team
        site.save()
        messages.success(request, "Site created successfully!")
        return redirect("analytics:index")
    return render(request, "sites/create.html", {"form": form})


@login_required
def edit_site(request, site_id):
    site = Site.objects.get(site_id=site_id, owner=request.user)
    if not site:
        messages.error(request, "Site not found.")
        return redirect("analytics:index")

    form = SiteCreationForm(request.POST or None, instance=site)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Site updated successfully!")
        return redirect("analytics:index")

    return render(request, "sites/edit.html", {"form": form, "site": site})


@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)
    if request.method == "POST":
        site.delete()
        messages.success(request, "Site deleted successfully.")
        return redirect("analytics:index")
    return render(request, "sites/delete.html", {"site": site})


@login_required
def send_verification(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)
    if not site.is_verified:
        verify_site.send(site.site_id)
        messages.success(request, "Verification task queued successfully.")
    else:
        messages.info(request, "Site is already verified.")
    return redirect("analytics:index")


@login_required
def site_details(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)

    # Pagination
    per_page = request.GET.get("per_page", 10)
    per_page = int(per_page) if str(per_page).isdigit() else 10
    page_number = request.GET.get("page")

    # Data fetching
    visitors = get_visitors(site)
    page_views_qs = get_page_views(site)
    top_pages = get_top_pages(site)
    top_referrers = get_top_referrers(site)
    chart_labels, chart_data = get_pageviews_by_day(site)

    paginator = Paginator(page_views_qs, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        "site": site,
        "visitors": visitors,
        "page_views": page_obj,
        "top_pages": top_pages,
        "top_referrers": top_referrers,
        "active_tab": "analytics",
        "page_number": page_number,
        "paginator": paginator,
        "page_obj": page_obj,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
    }
    return render(request, "sites/details.html", context)
