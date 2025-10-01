from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from apps.accounts.forms import (
    CustomAuthenticationForm,
    UserEditForm,
    UserProfileEditForm,
    UserSignupForm,
    UserActivationForm,
    UserActivationEmailChangeForm,
)
from apps.core.utils import get_or_null
from .models import UserActivation
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .tasks import send_user_activation_email


@login_required
def accounts_dashboard(request):
    """
    Render the user profile page for the authenticated user.
    Allows the user to edit their profile and user information.
    """
    uform = UserEditForm(request.POST or None or None, instance=request.user)
    pform = UserProfileEditForm(
        request.POST or None, request.FILES or None, instance=request.user.userprofile
    )

    if request.method == "POST" and uform.is_valid() and pform.is_valid():
        uform.save()
        pform.save()
        messages.success(request, "Userprofile updated successfully.")
        return redirect("accounts:index")

    return render(request, "accounts/index.html", {"uform": uform, "pform": pform})


def login_view(request):
    """
    Render the login page.
    """
    if request.user.is_authenticated:
        return redirect("analytics:index")
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("core:home")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    return redirect("core:home")


def register_view(request):
    """
    Render the first step of the user registration wizard.
    And send the activation email.
    """
    form = UserSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(
            request,
            "Registration successful! Please check your email for activation code.",
        )
        return redirect("accounts:activate")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def activate_view(request):
    """
    Render the second step of the user registration wizard.
    Handle user activation.
    """
    form = UserActivationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        activation_code = form.cleaned_data.get("activation_code")
        activation = get_or_null(
            UserActivation,
            user=request.user,
            activation_code=activation_code,
            is_active=False,
        )
        if activation:
            if activation.activate():
                messages.success(
                    request,
                    "Your account has been activated successfully!",
                )
                login(request, activation.user)
            else:
                messages.error(request, "Activation code is invalid or expired.")
            return redirect("analytics:index")
        else:
            messages.error(request, "Invalid activation code.")

    return render(request, "accounts/activate.html", {"form": form})


@login_required
def resend_activation_view(request):
    """
    Resend the activation email to the user.
    Also get the email from the user, if they want to change it.
    """
    form = UserActivationEmailChangeForm(
        request.POST or None, initial={"email": request.user.email}
    )
    if form.is_valid() and request.method == "POST":
        email = form.cleaned_data.get("email")
        if email:
            request.user.email = email
            request.user.save()
        send_user_activation_email.send(request.user.id)
        messages.success(
            request, "Activation email resent successfully! Please check your inbox."
        )
        return redirect("accounts:activate")
    return render(request, "accounts/resend_activation.html", {"form": form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import get_current_team
from django.contrib import messages


@login_required
def dashboard_index(request):
    """
    Render the dashboard page for authenticated users.
    """
    print(get_current_team(request))
    if get_current_team(request) is None:
        messages.info(request, "Please create a team to get started.")
        return redirect("teams:create")
    return render(request, "dashboard/index.html")


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Team, TeamMember, User
from .forms import TeamCreationForm, OwnershipTransferForm, TeamEditForm
from django.contrib import messages
from .utils import switch_team, get_user_teams, get_current_team


@login_required
@require_POST
def switch_team_view(request):
    """
    Switch the current team context for the user.
    """
    team_id = request.POST.get("team_id")
    path = request.POST.get("next", "dashboard:index")
    if not team_id:
        messages.error(request, "Invalid team selection.")
        return redirect(path)
    switch_team(request, team_id)
    return redirect(path)


@login_required
def team_create(request):
    """
    Render the team creation page.
    """
    form = TeamCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        team = form.save(commit=False)
        team.owner = request.user
        team.save()
        TeamMember.objects.create(user=request.user, team=team, role="admin")
        request.session["current_team_id"] = team.id
        messages.success(request, "Team created successfully!")
        return redirect("analytics:index")
    return render(request, "teams/create.html", {"form": form})


@login_required
def team_list(request):
    """
    List all teams the user is a member of.
    """
    teams = get_user_teams(request)
    if not teams:
        messages.info(request, "You are not a member of any teams.")
        return redirect("accounts:teams_create")
    current_team = get_current_team(request)
    return render(
        request, "teams/list.html", {"teams": teams, "current_team": current_team}
    )


@login_required
def team_details(request, slug):
    """
    View details of a specific team.
    """
    team = get_object_or_404(Team, slug=slug, members=request.user)
    return render(request, "teams/details.html", {"team": team})


@login_required
def team_transfer_ownership(request, slug):
    """
    Transfer ownership of a team to another user.
    """
    team = get_object_or_404(Team, slug=slug, owner=request.user)
    form = OwnershipTransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        new_owner_username = form.cleaned_data.get("new_owner")
        try:
            new_owner = User.objects.get(username=new_owner_username)
            team.transfer_ownership(new_owner)
            messages.success(request, "Ownership transferred successfully!")
            return redirect("accounts:teams_details", slug=team.slug)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
    return render(request, "teams/transfer.html", {"form": form, "team": team})


@login_required
def leave_team(request, slug):
    """
    Allow a user to leave a team.
    """
    team = get_object_or_404(Team, slug=slug, members=request.user)
    if request.method == "POST":
        TeamMember.objects.filter(user=request.user, team=team).delete()
        messages.success(request, "You have left the team.")
        return redirect("teams:list")
    return render(request, "teams/leave.html", {"team": team})


@login_required
def team_edit(request, slug):
    """
    Edit the details of a team.
    """
    team = get_object_or_404(Team, slug=slug, owner=request.user)
    form = TeamEditForm(
        instance=team, data=request.POST or None, files=request.FILES or None
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Team details updated successfully!")
        return redirect("accounts:teams_details", slug=team.slug)
    return render(request, "teams/edit.html", {"form": form, "team": team})


@login_required
def teams_over_limit(request):
    """
    Render the teams over limit page.
    """
    return render(request, "teams/over_limit.html")