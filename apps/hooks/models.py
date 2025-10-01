from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import secrets


""" 
{
  "id": "evt_4f8a9cce3c",                // Unique event ID
  "type": "form.submitted",              // Event type
  "timestamp": "2025-07-21T15:24:00Z",   // ISO 8601 UTC timestamp
  "team_id": "team_abc123",              // Originating team ID
  "site_id": "site_xyz789",              // (If relevant) site or form origin
  "data": {
    "form_id": "form_452bc1",
    "form_name": "Contact Us",
    "submission_id": "sub_3c1f91b",
    "submitted_at": "2025-07-21T15:23:55Z",
    "fields": {
      "name": "Jojo",
      "email": "jojo@example.com",
      "message": "Hey, I love your stuff!"
    },
    "ip": "123.45.67.89",                // Optional, if privacy allows
    "user_agent": "Mozilla/5.0..."       // Optional
  }
}
"""

def generate_event_id(prefix="evt_"):
    """
    Generates a unique event ID with a given prefix.
    """
    return f"{prefix}{secrets.token_urlsafe(8)}"

class WebhookEvent(models.Model):
    FORM_SUBMITTED = "form.submitted"
    TEAM_PLAN_CHANGED = "team.plan_changed"
    FORM_DELETED = "form.deleted"
    VISITOR_SESSION = "visitor.session"
    EVENT_TYPES = [
        (FORM_SUBMITTED, "Form Submitted"),
        (TEAM_PLAN_CHANGED, "Team Plan Changed"),
        (FORM_DELETED, "Form Deleted"),
        (VISITOR_SESSION, "Visitor Session"),
    ]

    id = models.CharField(max_length=64, primary_key=True, editable=False, default=generate_event_id)
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
