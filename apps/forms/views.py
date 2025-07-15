from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from .forms import PingFoxFormCreatationForm, DynamicFormSchemaForm
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponseBadRequest
from django.contrib import messages
from apps.forms.utils import (
    convert_form_to_schema,
    create_form_class_from_schema,
    create_form_from_form_model,
)

from apps.teams.utils import get_current_team


@login_required
def form_index(request):
    """
    Render the form index page for the authenticated user.
    """
    return redirect("forms:list")


@login_required
def form_list(request):
    """
    Render the list of forms for the authenticated user.
    """
    # Fetch forms created by the user or associated with their team
    team = get_current_team(request)
    forms = team.forms.all()
    max_forms = team.get_limit("forms")
    return render(request, "forms/list.html", {"forms": forms, "team": team, "max_forms": max_forms})


@login_required
def form_create(request):
    """
    Render the form creation page for the authenticated user.
    """
    # Get the currently selected team for the user session
    team = get_current_team(request)
    if team.is_limit_exceeded("forms"):
        messages.error(
            request, "You have reached the limit for creating forms in this team."
        )
        return redirect("forms:list")
    form = PingFoxFormCreatationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(commit=False)
        form.ownder = request.user

        messages.success(request, "Form created successfully.")
        return redirect("forms:builder", slug=form.slug)

    return render(request, "forms/create.html", {"form": form})


@login_required
def form_edit(request, slug):
    """
    Render the form edit page for the authenticated user.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    if request.method == "POST":
        form_form = PingFoxFormCreatationForm(request.POST, instance=form)
        if form_form.is_valid():
            form_form.save()
            messages.success(request, "Form updated successfully.")
            return redirect("forms:builder", slug=form.slug)
    else:
        form_form = PingFoxFormCreatationForm(instance=form)

    return render(request, "forms/edit.html", {"form": form_form})


@login_required
def form_builder(request, slug):
    """
    Render the form builder page for the authenticated user.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug)
    ui = create_form_from_form_model(form)
    if request.method == "POST":
        # Handle form submission logic here
        pass
    return render(
        request,
        "forms/builder.html",
        {"form": form, "ui": ui},
    )


@login_required
def form_editor(request, slug):
    """
    Render the form editor page for the authenticated user.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)
    schema = convert_form_to_schema(form)

    if request.method == "POST":
        schema_json = request.POST.get("schema")
        if not schema_json:
            messages.error(request, "Schema is required.")
            return redirect("forms:editor", slug=slug)

    return render(
        request,
        "forms/editor.html",
        {"form": form, "schema": json.dumps(schema, indent=2)},
    )


@login_required
@require_POST
def convert_schema_to_form_view(request):
    """
    Convert a schema definition to a Django form class.
    """
    schema = DynamicFormSchemaForm(request.POST)
    if not schema.is_valid():
        return HttpResponseBadRequest("Invalid schema format.")
    form_class = schema.convert()
    return render(
        request, "forms/partials/form_fragment.html", {"form_class": form_class}
    )
