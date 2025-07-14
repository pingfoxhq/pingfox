from django import forms

from .models import Form

class PingFoxFormCreatationForm(forms.ModelForm):
    """
    Form for creating a new form.
    """
    class Meta:
        model = Form
        fields = ['name', 'description', 'authentication_required']