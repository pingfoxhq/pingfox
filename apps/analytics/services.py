from .models import PageView
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncHour, TruncMinute
from django.utils import timezone

def get_site_analytics(site, range="daily"):
    now = timezone.now()
    qs = PageView.objects.filter(site=site)

    if range == "daily":
        raw_data = (
            qs.filter(timestamp__gte=now - timezone.timedelta(days=30))
              .annotate(label=TruncDay("timestamp"))
              .values("label")
              .annotate(count=Count("id"))
              .order_by("label")
        )
        formatter = lambda dt: dt.strftime("%b %d")  # e.g. "Jul 17"

    elif range == "hourly":
        raw_data = (
            qs.filter(timestamp__gte=now - timezone.timedelta(days=2))
              .annotate(label=TruncHour("timestamp"))
              .values("label")
              .annotate(count=Count("id"))
              .order_by("label")
        )
        formatter = lambda dt: dt.strftime("%H:%M")  # e.g. "14:00"

    elif range == "minute":
        raw_data = (
            qs.filter(timestamp__gte=now - timezone.timedelta(hours=1))
              .annotate(label=TruncMinute("timestamp"))
              .values("label")
              .annotate(count=Count("id"))
              .order_by("label")
        )
        formatter = lambda dt: dt.strftime("%H:%M")  # e.g. "14:52"

    else:
        return []

    # Format timestamps before returning
    return [
        {
            "label": formatter(row["label"]),
            "count": row["count"]
        }
        for row in raw_data
    ]
