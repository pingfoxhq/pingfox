from django.forms import ModelForm
from .models import Site

class SiteCreationForm(ModelForm):
    class Meta:
        model = Site
        fields = ["name", "domain", "timezone"]