from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ChangePlanForm, RedeemCodeForm
from .models import Plan, RedeemCode, CodeRedemption
from django.contrib import messages
from apps.accounts.utils import get_current_team


@login_required
def change_plan(request):
    """
    View to change the billing plan of the user.
    """
    team = get_current_team(request)
    if team.owner != request.user:
        messages.error(
            request, "You do not have permission to change the billing plan."
        )
        return redirect("accounts:teams_details", team_id=team.slug)
    plans = Plan.objects.filter(is_active=True, visible=True)
    if request.method == "POST":
        # Handle form submission for changing the plan
        form = ChangePlanForm(request.POST)
        if form.is_valid():
            # Process the form data and change the plan
            # :TODO: Add logic to handle plan change
            # For now, we will do nothing and just show a success message
            # For now, we will just use the redeem code form for the payment
            messages.success(request, "Billing plan change request submitted.")
            return redirect("billing:change_plan")
            new_plan = form.cleaned_data["plan"]
            team.plan = new_plan
            team.save()
            messages.success(
                request, f"Successfully changed the billing plan to {new_plan.name}."
            )
            return redirect("billing:change_plan")
    else:
        # Display the form for changing the plan
        form = ChangePlanForm()
    redeem_code_form = RedeemCodeForm()
    return render(
        request,
        "billing/change_plan.html",
        {
            "form": form,
            "plans": plans,
            "team": team,
            "redeem_code_form": redeem_code_form,
        },
    )


@login_required
def redeem_code(request):
    """
    View to redeem a billing code.
    """
    team = get_current_team(request)
    form = RedeemCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]
        try:
            redeem_code = RedeemCode.objects.get(code=code)
            if redeem_code.is_valid():
                CodeRedemption.objects.create(
                    redeem_code=redeem_code,
                    user=request.user,
                    team=team,
                )
                messages.success(request, "Code redeemed successfully!")
            else:
                messages.error(request, "This code is not valid or has expired.")
        except RedeemCode.DoesNotExist:
            messages.error(request, "The ")
    return redirect("billing:change_plan")
