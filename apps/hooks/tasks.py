# billing/tasks.py

import requests
import json
import dramatiq
from django.utils import timezone
from .models import WebhookEvent
from .serializers import WebhookEventSerializer
from utils import generate_webhook_signature

@dramatiq.actor
def deliver_webhook(event_id: str, webhook_url: str, secret: str):
    try:
        event = WebhookEvent.objects.get(id=event_id)
        serializer = WebhookEventSerializer(event)
        payload_json = json.dumps(serializer.data, default=str)

        signature = generate_webhook_signature(payload_json, secret)

        response = requests.post(
            webhook_url,
            data=payload_json,
            headers={
                "Content-Type": "application/json",
                "X-PingFox-Signature": f"sha256={signature}",
            },
            timeout=5,
        )

        event.delivered = response.status_code < 400
        event.last_delivery_status = f"{response.status_code}: {response.text[:200]}"
    except Exception as e:
        event.delivered = False
        event.last_delivery_status = f"Error: {str(e)}"
    finally:
        event.delivery_attempts += 1
        event.save(update_fields=["delivered", "last_delivery_status", "delivery_attempts"])
