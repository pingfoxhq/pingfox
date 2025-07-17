from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import VisitorSession, PageView
import uuid
from apps.sites.models import Site
import json

# disable cors

def cors_enabled(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    return wrapper


@csrf_exempt
@cors_enabled
def collect_data(request):
    if request.method == "POST":
        # Process the data sent from the client
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
        print(f"Received data: {request.POST}")  # Debugging line to see the incoming data
        # Here you would typically save the data to your database or perform some action
        # Lets start processing the data
        # First create a VisitorSession
        pf_id = data.get("pf_id")
        site_id = data.get("site_id")
        if not site_id:
            return JsonResponse({"status": "error", "message": "Site ID is required."}, status=400)
        
        # Get the site from the site_id
        site = get_object_or_404(Site, site_id=site_id)
        if not pf_id:
            # Generate a new pf_id if not provided
            pf_id = str(uuid.uuid4())
        visitor_session, created = VisitorSession.objects.get_or_create(
            pf_id=pf_id,
        )
        # Update the visitor session with the user agent and other data
        visitor_session.user_agent = data.get("ua", "")
        # visitor_session.last_seen = data.get("last_seen", None) # Optional: Update last seen if provided
        visitor_session.timestamp = data.get("ts", None)  # Optional: Update timestamp if provided
        visitor_session.save()

        # Create a PageView entry
        page_view = PageView.objects.create(
            visitor=visitor_session,
            site=site,
            url=data.get("url", ""),
            referrer=data.get("referrer", ""),
            screen_width=data.get("width", ""),
            screen_height=data.get("height", ""),
        )
        # Return a success response
        response_data = {
            "status": "success",
            "message": "Data collected successfully.",
            "visitor_id": visitor_session.pf_id,
            "page_view_id": page_view.id,
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)