from django import forms

from .models import Form
from django import forms
from django import forms
from django.core.validators import RegexValidator


def create_form_class_from_schema(schema):
    fields = {}
    existing_names = set()
    for index, field in enumerate(schema):
        label = field.get("label", "Field")
        base_name = field.get("name") or label.lower().replace(" ", "_")
        name = base_name

        # Ensure uniqueness
        counter = 1
        while name in existing_names:
            name = f"{base_name}_{counter}"
            counter += 1
        existing_names.add(name)

        field_type = field.get("type", "text")
        required = field.get("required", False)
        options = field.get("options", None)
        validation_regex = field.get("validation")
        help_text = field.get("helpText", "")
        default_value = field.get("defaultValue", "")
        validators = []
        if validation_regex:
            validators.append(
                RegexValidator(
                    regex=validation_regex, message=f"Invalid input for {label}"
                )
            )

        # Create appropriate field
        if (field_type == "dropdown" or field_type == "select") and options:
            fields[name] = forms.ChoiceField(
                label=label,
                required=required,
                choices=[(opt, opt) for opt in options],
                widget=forms.Select,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "text":
            fields[name] = forms.CharField(
                label=label,
                required=required,
                widget=forms.TextInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "textarea":
            fields[name] = forms.CharField(
                label=label,
                required=required,
                widget=forms.Textarea(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "email":
            fields[name] = forms.EmailField(
                label=label,
                required=required,
                widget=forms.EmailInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "number":
            fields[name] = forms.IntegerField(
                label=label,
                required=required,
                widget=forms.NumberInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "date":
            fields[name] = forms.DateField(
                label=label,
                required=required,
                widget=forms.DateInput(attrs={"placeholder": label, "type": "date"}),
                validators=validators,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "checkbox":
            fields[name] = forms.BooleanField(
                label=label,
                required=required,
                help_text=help_text,
                initial=default_value,
            )
        elif field_type == "radio":
            fields[name] = forms.ChoiceField(
                label=label,
                required=required,
                choices=[(opt, opt) for opt in options] if options else [],
                widget=forms.RadioSelect,
                help_text=help_text,
                initial=default_value,
            )
        else:
            fields[name] = forms.CharField(
                label=label,
                required=required,
                widget=forms.TextInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
                initial=default_value,
            )

    return type("DynamicForm", (forms.Form,), fields)


def create_form_from_form_model(form: Form):
    """
    Create a Django form class from a Form model instance.
    """
    schema = [
        {
            "label": field.label,
            "required": field.required,
            "type": field.field_type,
            "options": field.choices.split(",") if field.choices else None,
            "validation_regex": field.validation_regex,
            "help_text": field.help_text,
        }
        for field in form.fields.all()
    ]

    return create_form_class_from_schema(schema)


def convert_form_to_schema(form: Form):
    """
    Convert a Django form class to a schema definition.
    """
    schema = [
        {
            "label": field.label,
            "required": field.required,
            "type": field.field_type,
            "options": field.choices.split(",") if field.choices else None,
            "validation_regex": field.validation_regex,
            "help_text": field.help_text,
        }
        for field in form.fields.all()
    ]
    return schema
