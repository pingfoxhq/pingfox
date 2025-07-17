from django import forms

from .models import Form, FormStyle
from .utils import create_form_class_from_schema, convert_form_to_schema


class PingFoxFormCreatationForm(forms.ModelForm):
    """
    Form for creating a new form.
    """

    class Meta:
        model = Form
        fields = [
            "name",
            "description",
            "redirect_url",
            "authentication_required",
            "auth_key",
            "is_active",
            "allow_multiple_submissions",
            "allow_analytics",
            "button_text",
        ]

class DynamicFormSchemaForm(forms.Form):
    """
    Form for dynamically creating a form based on a schema.
    """

    schema = forms.JSONField(
        label="Form Schema", help_text="Provide a JSON schema to create a dynamic form."
    )

    def convert(self):
        """
        Convert the provided schema into a Django form class.
        """
        schema = self.cleaned_data.get("schema")
        if not schema:
            raise forms.ValidationError("Schema is required.")

        return create_form_class_from_schema(schema)

class FormStyleForm(forms.ModelForm):
    """
    Form for creating or updating a form style.
    """

    class Meta:
        model = FormStyle
        fields = [
            "background_color",
            "text_color",
            "accent_color",
            "button_color",
            "button_text_color",
            "font_family",
            "logo",
            "custom_css",
        ]
        widgets = {
            "custom_css": forms.Textarea(attrs={"rows": 10, "cols": 80}),
        }

    def clean_custom_css(self):
        custom_css = self.cleaned_data.get("custom_css")
        if custom_css and not custom_css.strip():
            raise forms.ValidationError("Custom CSS cannot be empty.")
        return custom_css