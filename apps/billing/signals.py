from django.dispatch import receiver
from django.db.models.signals import post_migrate


from apps.billing.models import Plan, PlanFeature
from apps.billing.seed import BASE_FREE_PLAN, DEFAULT_FEATURES

@receiver(post_migrate)
def create_base_free_plan(sender, **kwargs):
    plan, _created = Plan.objects.get_or_create(**BASE_FREE_PLAN)
    for key, value in DEFAULT_FEATURES.items():
        PlanFeature.objects.get_or_create(plan=plan, key=key, defaults={"value": value})