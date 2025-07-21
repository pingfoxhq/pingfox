from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required

from apps.analytics.models import VisitorSession
from .forms import PingFoxFormCreatationForm, DynamicFormSchemaForm, FormStyleForm
from django.contrib import messages
from .models import Form, FormSubmission
from django.views.decorators.http import require_POST
import json
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.contrib import messages
from apps.forms.utils import (
    convert_form_to_schema,
    create_form_from_form_model,
    get_pf_id,
)

from apps.accounts.utils import get_current_team


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
    return render(
        request,
        "forms/list.html",
        {"forms": forms, "team": team, "max_forms": max_forms},
    )


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
        form_obj = form.save(commit=False)
        form_obj.owner = request.user
        form_obj.team = team
        form_obj.save()
        messages.success(request, "Form created successfully.")
        return redirect("forms:builder", slug=form_obj.slug)

    return render(request, "forms/create.html", {"form": form})


@login_required
def form_edit(request, slug):
    """
    Render the form edit page for the authenticated user.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    form_form = PingFoxFormCreatationForm(request.POST or None, instance=form)
    style_form = FormStyleForm(request.POST or None, instance=form.style)
    if request.method == "POST" and form_form.is_valid():
        form_form.save()
        messages.success(request, "Form updated successfully.")
        return redirect("forms:list")

    return render(
        request,
        "forms/edit.html",
        {"form": form_form, "style_form": style_form, "form_obj": form},
    )


@login_required
def form_delete(request, slug):
    """
    Handle the deletion of a form.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    if request.method == "POST":
        form.delete()
        messages.success(request, "Form deleted successfully.")
        return redirect("forms:list")
    form_class = create_form_from_form_model(form)
    return render(request, "forms/delete.html")


@login_required
def form_builder(request, slug):
    """
    Render the form builder page for the authenticated user.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug)

    if form.is_locked:
        messages.error(request, "Form is locked and cannot be edited.")
        return redirect(
            "forms:list",
        )

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


@require_POST
@login_required
def save_form(request, slug):
    """
    Save the form schema from the editor.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    if form.is_locked:
        return HttpResponseBadRequest("Form is locked and cannot be edited.")

    try:
        data = json.loads(request.body)
        schema = data.get("fields", [])

        if not isinstance(schema, list):
            return JsonResponse({"error": "Invalid schema format"}, status=400)

        # Delete old fields
        form.fields.all().delete()

        # Save each new field
        for field in schema:
            form.fields.create(
                label=field["label"],
                required=field.get("required", False),
                field_type=field.get("type", "text"),
                choices=",".join(field["options"]) if field.get("options") else "",
                validation_regex=field.get("validation", ""),
                help_text=field.get("help_text", ""),
                order=field.get("order", 0),
                name=field.get("name", "").strip(),
                placeholder=field.get("placeholder", field["label"]),
                hidden=field.get("hidden", False),
                disabled=field.get("disabled", False),
                readonly=field.get("readonly", False),
                default_value=field.get("default_value", ""),
            )

        return JsonResponse({"status": "success"})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def save_form_schema_view(request, slug):
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    if form.is_locked:
        return HttpResponseBadRequest("Form is locked and cannot be edited.")

    schema_json = request.POST.get("schema")

    if not schema_json:
        return HttpResponseBadRequest("Schema is required.")

    try:
        schema = json.loads(schema_json)
        form.fields.all().delete()
        for field in schema:
            form.fields.create(
                label=field["label"],
                required=field["required"],
                field_type=field["type"],
                choices=",".join(field["options"]) if field.get("options") else "",
                validation_regex=field.get("validation", ""),
                help_text=field.get("help_text", ""),
                name=field.get("name", "").strip(),
                placeholder=field.get("placeholder", field["label"]),
                hidden=field.get("hidden", False),
                disabled=field.get("disabled", False),
                readonly=field.get("readonly", False),
                default_value=field.get("default_value", ""),
            )
        return HttpResponse("✅ Schema saved successfully.")
    except Exception as e:
        return HttpResponseBadRequest(f"Error saving schema: {str(e)}")


def form_public_view(request, slug):
    """
    Render a public view of the form.
    This is just for the view.
    The Submission endpoint is handled separately.
    """
    form_obj = get_object_or_404(Form, slug=slug, is_active=True)
    form_class = create_form_from_form_model(form_obj)
    form = form_class()
    return render(
        request,
        "forms/public_form.html",
        {
            "form": form,
            "form_obj": form_obj,
        },
    )


@require_POST
def form_submit_view(request, slug):
    form_obj = get_object_or_404(Form, slug=slug)
    pf_id = get_pf_id(request)
    if not form_obj.is_active:
        return HttpResponseBadRequest("This form is not active or does not exist.")

    if not form_obj.allow_multiple_submissions:
        # Check if the visitor has already submitted the form
        visitor = form_obj.visitors.filter(pf_id=pf_id).first()
        if visitor:
            return HttpResponseBadRequest(
                "You have already submitted this form. Multiple submissions are not allowed."
            )

    # The Main Part
    form_class = create_form_from_form_model(form_obj)
    form = form_class(request.POST)
    if form.is_valid():
        FormSubmission.objects.create(
            form=form_obj,
            data=form.cleaned_data,
        )
        # Lock the form to prevent further submissions
        form_obj.is_locked = True
        form_obj.save()

        # Add the visitor to the form's visitors
        visitor, created = VisitorSession.objects.get_or_create(
            pf_id=pf_id,
            defaults={"user_agent": request.META.get("HTTP_USER_AGENT", "")},
        )
        form_obj.visitors.add(visitor)

        if form_obj.redirect_url:
            return redirect(form_obj.redirect_url)
        return render(request, "forms/thank_you.html", {"form_obj": form_obj})
    return render(
        request,
        "forms/public_form.html",
        {
            "form_obj": form_obj,
            "form": form,
            "errors": form.errors,
        },
    )


@login_required
def form_schema(request, slug):
    """
    Get the schema of a form as JSON.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug)
    schema = convert_form_to_schema(form)
    return JsonResponse(schema, safe=False)


@login_required
def freeze_form(request, slug):
    """
    Freeze the form to prevent further schame edits.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    if form.is_locked:
        messages.error(request, "Form is already locked.")
        return redirect("forms:editor", slug=slug)

    if request.method == "POST":
        form.is_locked = True
        form.save()
        messages.success(request, "Form has been locked successfully.")
        return redirect("forms:list")
    return render(request, "forms/freeze_form.html", {"form": form})


@login_required
def submission_table_view(request, slug):
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)
    submissions = form.submissions.all()

    # Collect all field names from the first submission (or union of all fields)
    field_labels = []
    if submissions:
        all_keys = set()
        for s in submissions:
            all_keys.update(s.data.keys())
        field_labels = sorted(all_keys)

    return render(
        request,
        "forms/submissions_table.html",
        {
            "form": form,
            "submissions": submissions,
            "field_labels": field_labels,
        },
    )


@login_required
def style_update(request, slug):
    """
    Update the form style.
    """
    team = get_current_team(request)
    form = get_object_or_404(team.forms, slug=slug, owner=request.user)

    style_form = FormStyleForm(request.POST, request.FILES or None, instance=form.style)
    if request.method == "POST" and style_form.is_valid():
        style_form.save()
        messages.success(request, "Form style updated successfully.")
        return redirect("forms:edit", slug=slug)
    # Just redirect the edit page with the style form
    messages.error(request, "Failed to update form style. Please check the form.")
    if not style_form.errors:
        messages.error(request, "No changes were made to the style.")
    # Redirect to the edit page with the form and style form
    return redirect("forms:edit", slug=slug)
