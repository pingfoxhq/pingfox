from .models import Plan

def pricing_plans(request):
    """
    Context processor to add active pricing plans to the context.
    """
    active_plans = Plan.objects.filter(is_active=True).order_by('ranking', 'name')
    return {
        'active_pricing_plans': active_plans
    }