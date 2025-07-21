from django.dispatch import receiver
from django.db.models.signals import post_migrate, post_save


from apps.billing.models import Plan, PlanFeature, RedeemCode, CodeRedemption
from apps.billing.seed import BASE_FREE_PLAN, DEFAULT_FEATURES


@receiver(post_migrate)
def create_base_free_plan(sender, **kwargs):
    plan, _created = Plan.objects.get_or_create(**BASE_FREE_PLAN)
    for key, value in DEFAULT_FEATURES.items():
        PlanFeature.objects.get_or_create(plan=plan, key=key, defaults={"value": value})


@receiver(post_save, sender=CodeRedemption)
def update_redeem_code(sender, instance, created, **kwargs):
    """
    Update the redeem code status after a redemption is created.
    """
    if created:
        redeem_code = instance.redeem_code
        instance.team.plan = redeem_code.plan
        redeem_code.used_count += 1
        if (
            redeem_code.usage_limit
            and redeem_code.used_count >= redeem_code.usage_limit
        ):
            redeem_code.is_active = False
        instance.team.save()
        redeem_code.save()
