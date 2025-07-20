from django.dispatch import receiver
from django.db.models.signals import post_migrate


from apps.billing.models import Plan
from apps.billing.seed import BASE_FREE_PLAN

@receiver(post_migrate)
def create_base_free_plan(sender, **kwargs):
    if sender == Plan:
        Plan.objects.get_or_create(**BASE_FREE_PLAN)