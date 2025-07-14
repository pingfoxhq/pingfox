from django.forms import ModelForm, CharField, TextInput
from apps.teams.models import Team


class TeamCreationForm(ModelForm):
    """
    Form for creating a new team.
    """

    name = CharField(
        max_length=100,
        help_text="Enter the name of your team.",
        widget=TextInput(attrs={"placeholder": "Team Name"}),
    )

    class Meta:
        model = Team
        fields = [
            "name",
        ]
