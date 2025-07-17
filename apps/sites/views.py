from django.shortcuts import render, redirect, get_object_or_404
from .forms import SiteCreationForm
from django.contrib.auth.decorators import login_required
from .models import Site
from django.contrib import messages
from apps.analytics.models import VisitorSession, PageView
from django.core.paginator import Paginator
from django.db.models import Count
from apps.teams.utils import get_current_team
from .tasks import verify_site


@login_required
def index(request):
    return redirect("sites:list")


@login_required
def list_sites(request):
    team = get_current_team(request)
    sites = team.sites.all() if team else Site.objects.none()
    max_sites = team.feature_limit("sites_limit") if team else 1
    # Check if the team has reached the limit for sites
    can_create = not team.is_limit_exceeded("sites") if team else True
    return render(
        request,
        "sites/list.html",
        {"sites": sites, "max_sites": max_sites, "can_create": can_create},
    )


@login_required
def create_site(request):

    team = get_current_team(request)
    if team.is_limit_exceeded("sites"):
        messages.error(
            request,
            "You have reached the maximum number of sites allowed for your team.",
        )
        return redirect("sites:list")

    form = SiteCreationForm(request.POST or None, initial={"user": request.user})
    if request.method == "POST" and form.is_valid():
        site: Site = form.save(commit=False)
        site.owner = request.user
        site.team = team
        site.save()
        messages.success(request, "Site created successfully!")
        return redirect("sites:index")
    return render(request, "sites/create.html", {"form": form})


@login_required
def edit_site(request, site_id):
    site = Site.objects.get(site_id=site_id, owner=request.user)
    if not site:
        messages.error(request, "Site not found.")
        return redirect("sites:list")

    form = SiteCreationForm(request.POST or None, instance=site)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Site updated successfully!")
        return redirect("sites:list")

    return render(request, "sites/edit.html", {"form": form, "site": site})


@login_required
def send_verification(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)
    if not site.is_verified:
        verify_site.send(site.site_id)
        messages.success(request, "Verification task queued successfully.")
    else:
        messages.info(request, "Site is already verified.")
    return redirect("sites:list")


@login_required
def delete_site(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)
    if request.method == "POST":
        site.delete()
        messages.success(request, "Site deleted successfully.")
        return redirect("sites:list")
    return render(request, "sites/delete.html", {"site": site})


@login_required
def site_details(request, site_id):
    site = get_object_or_404(Site, site_id=site_id, owner=request.user)

    visitors = VisitorSession.objects.filter(page_views__site=site).distinct()

    page_views = PageView.objects.filter(site=site).order_by("-timestamp")

    # Pagination for page views
    per_page = request.GET.get("per_page", 10)
    if str(per_page).isdigit():
        per_page = int(per_page)
    else:
        per_page = 10
    paginator = Paginator(page_views, per_page)  # Show per_page page views per page

    top_pages = (
        PageView.objects.filter(site=site)
        .values("url")
        .annotate(view_count=Count("id"))
        .order_by("-view_count")[:5]
    )

    top_referrers = (
        PageView.objects.filter(site=site)
        .exclude(referrer__isnull=True)
        .exclude(referrer__exact="")
        .values("referrer")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )
    page_number = request.GET.get("page")
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
        "visitor_count": visitors.count(),
        "page_view_count": page_views.count(),
        "top_referrer_count": top_referrers.count(),
        "top_page_count": top_pages.count(),
    }
    return render(request, "sites/details.html", context)
