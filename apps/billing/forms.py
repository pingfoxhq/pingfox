from django import forms
from .models import Plan


class ChangePlanForm(forms.Form):
    """
    Form for changing the billing plan.
    """
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.filter(is_active=True, visible=True),
        label="Select a Plan",
        help_text="Choose a billing plan to switch to.",
        empty_label="Select a plan",
        required=True,
    )

class RedeemCodeForm(forms.Form):
    """
    Form for redeeming a billing code.
    """
    code = forms.CharField(
        max_length=100,
        label="Redeem Code",
        help_text="Enter your billing code to redeem.",
        required=True,
    )