from django import forms

from .models import Form
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
            "is_active",
            "allow_multiple_submissions",
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
