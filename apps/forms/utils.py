from django import forms

from .models import Form
from django import forms
from django import forms
from django.core.validators import RegexValidator


def create_form_class_from_schema(schema):
    fields = {}
    for field in schema:
        print(field)
        label = field.get("label", "Field")
        required = field.get("required", False)
        field_type = field.get("type", "text")  # default to text
        options = field.get("options", None)
        validation_regex = field.get("validation_regex")
        help_text = field.get("help_text", "")
        validators = []
        if validation_regex:
            validators.append(
                RegexValidator(
                    regex=validation_regex, message=f"Invalid input for {label}"
                )
            )

        if (field_type == "dropdown" or field_type == "select") and options:
            fields[label] = forms.ChoiceField(
                label=label,
                required=required,
                choices=[(opt, opt) for opt in options],
                widget=forms.Select,
                help_text=help_text,
            )
        elif field_type == "text":
            fields[label] = forms.CharField(
                label=label,
                required=required,
                widget=forms.TextInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
            )
        elif field_type == "textarea":
            fields[label] = forms.CharField(
                label=label,
                required=required,
                widget=forms.Textarea(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
            )
        elif field_type == "email":
            fields[label] = forms.EmailField(
                label=label,
                required=required,
                widget=forms.EmailInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
            )
        elif field_type == "number":
            fields[label] = forms.IntegerField(
                label=label,
                required=required,
                widget=forms.NumberInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
            )
        elif field_type == "date":
            fields[label] = forms.DateField(
                label=label,
                required=required,
                widget=forms.DateInput(attrs={"placeholder": label, "type": "date"}),
                validators=validators,
                help_text=help_text,
            )
        elif field_type == "checkbox":
            fields[label] = forms.BooleanField(
                label=label,
                required=required,
                widget=forms.CheckboxInput(),
                help_text=help_text,
            )
        else:
            # fallback to simple CharField text input
            fields[label] = forms.CharField(
                label=label,
                required=required,
                widget=forms.TextInput(attrs={"placeholder": label}),
                validators=validators,
                help_text=help_text,
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
