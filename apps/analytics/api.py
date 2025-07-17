from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorSession, PageView
import uuid
from apps.sites.models import Site
import json
from django.contrib.auth.decorators import login_required
from apps.analytics.services import get_site_analytics
from apps.core.utils import cors_enabled


@csrf_exempt
@cors_enabled
def collect_data(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
        pf_id = data.get("pf_id")
        site_id = data.get("site_id")
        if not site_id:
            return JsonResponse(
                {"status": "error", "message": "Site ID is required."}, status=400
            )
        site = get_object_or_404(Site, site_id=site_id)
        if not pf_id:
            pf_id = str(uuid.uuid4())
        visitor_session, created = VisitorSession.objects.get_or_create(
            pf_id=pf_id,
        )
        visitor_session.user_agent = data.get("ua", "")
        visitor_session.timestamp = data.get(
            "ts", None
        )  # Optional: Update timestamp if provided
        visitor_session.save()
        page_view = PageView.objects.create(
            visitor=visitor_session,
            site=site,
            url=data.get("url", ""),
            referrer=data.get("referrer", ""),
            screen_width=data.get("width", ""),
            screen_height=data.get("height", ""),
        )
        response_data = {
            "status": "success",
            "message": "Data collected successfully.",
            "visitor_id": visitor_session.pf_id,
            "page_view_id": page_view.id,
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."}, status=400
        )


@login_required
def site_chart_data_api(request, site_id):
    """
    API endpoint to get site analytics data for charts.
    """
    site = get_object_or_404(Site, site_id=site_id)
    range = request.GET.get("range", "daily")
    data = get_site_analytics(site, range)
    return JsonResponse(data, safe=False, status=200)
