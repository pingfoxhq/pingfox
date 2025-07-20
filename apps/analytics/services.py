from django.db.models import Count
from django.db.models.functions import TruncDay, TruncHour, TruncMinute
from django.utils import timezone
from apps.analytics.models import PageView, VisitorSession


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
        {"label": formatter(row["label"]), "count": row["count"]} for row in raw_data
    ]


def get_top_pages(site, limit=5):
    return (
        PageView.objects.filter(site=site)
        .values("url")
        .annotate(view_count=Count("id"))
        .order_by("-view_count")[:limit]
    )


def get_top_referrers(site, limit=5):
    return (
        PageView.objects.filter(site=site)
        .exclude(referrer__isnull=True)
        .exclude(referrer__exact="")
        .values("referrer")
        .annotate(count=Count("id"))
        .order_by("-count")[:limit]
    )


def get_pageviews_by_day(site, days=14):
    now = timezone.now()
    qs = (
        PageView.objects.filter(
            site=site, timestamp__gte=now - timezone.timedelta(days=days)
        )
        .annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    return [entry["day"].strftime("%Y-%m-%d") for entry in qs], [
        entry["count"] for entry in qs
    ]


def get_visitors(site):
    return VisitorSession.objects.filter(page_views__site=site).distinct()


def get_page_views(site):
    return PageView.objects.filter(site=site).order_by("-timestamp")


def get_view_stats(site):
    now = timezone.now()

    daily = (
        PageView.objects.filter(
            site=site, timestamp__gte=now - timezone.timedelta(days=30)
        )
        .annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    hourly = (
        PageView.objects.filter(
            site=site, timestamp__gte=now - timezone.timedelta(days=2)
        )
        .annotate(hour=TruncHour("timestamp"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("hour")
    )

    per_minute = (
        PageView.objects.filter(
            site=site, timestamp__gte=now - timezone.timedelta(hours=1)
        )
        .annotate(minute=TruncMinute("timestamp"))
        .values("minute")
        .annotate(count=Count("id"))
        .order_by("minute")
    )

    return {
        "daily": list(daily),
        "hourly": list(hourly),
        "per_minute": list(per_minute),
    }
