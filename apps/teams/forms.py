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

class OwnershipTransferForm(ModelForm):
    """
    Form for transferring ownership of a team.
    """

    new_owner = CharField(
        max_length=150,
        help_text="Enter the username of the new team owner.",
        widget=TextInput(attrs={"placeholder": "New Owner Username"}),
    )

    class Meta:
        model = Team
        fields = [
            "new_owner",
        ]
