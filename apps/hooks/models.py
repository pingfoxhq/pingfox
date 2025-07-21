from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class WebhookEvent(models.Model):
    EVENT_TYPES = [
        ("form.submitted", "Form Submitted"),
        ("team.plan_changed", "Team Plan Changed"),
        ("form.deleted", "Form Deleted"),
        ("visitor.session", "Visitor Session"),
    ]

    id = models.CharField(max_length=64, primary_key=True)
    type = models.CharField(max_length=64, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)

    team_id = models.CharField(max_length=64)
    site_id = models.CharField(max_length=64, blank=True, null=True)

    data = models.JSONField()

    delivered = models.BooleanField(default=False)
    delivery_attempts = models.PositiveIntegerField(default=0)
    last_delivery_status = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.type} ({self.id})"
