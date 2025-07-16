from django.db import models
from apps.accounts.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django_resized import ResizedImageField
from apps.billing.models import Plan


class Team(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Team Name"),
        help_text=_("The name of the team, must be unique."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("Team Slug"),
        help_text=_("A unique identifier for the team, used in URLs."),
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        related_name="teams",
        verbose_name=_("Plan"),
        help_text=_("The billing plan associated with the team."),
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_teams",
        verbose_name=_("Team Owner"),
        help_text=_("The user who owns the team."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the team was created."),
    )
    members = models.ManyToManyField(
        User,
        through='TeamMember',
        related_name="teams",
        verbose_name=_("Team Members"),
        help_text=_("Users who are members of the team."),
    )

    logo = ResizedImageField(
        upload_to="uploads/team_logos/",
        size=[200, 200],
        crop=["middle", "center"],
        quality=90,
        verbose_name=_("Team Logo"),
        null=True,
        blank=True,
        help_text=_("Team's logo, resized to 200x200 pixels."),
        default="defaults/team_logo.png",
    )

    def __str__(self):
        return self.name
    
    def feature_limit(self, feature_name):
        """
        Get the limit for a specific feature based on the team's plan.
        """
        if self.plan and self.plan.get_feature(feature_name) is not None:
            return self.plan.get_feature(feature_name)
        else:
            return None
        
    def is_limit_exceeded(self, resource_type):
        from apps.forms.models import Form  # adjust import to avoid circular

        if resource_type == "forms":
            max_allowed = int(self.feature_limit("forms_limit")) or 3
            current_count = self.forms.count()
            return max_allowed is not None and current_count >= max_allowed

        # You can add more like 'members', 'integrations', etc.
        return False


    def transfer_ownership(self, new_owner):
        """
        Transfer ownership of the team to a new user.
        """
        if not isinstance(new_owner, User):
            raise ValueError(_("New owner must be a User instance."))

        # Change the role of the old owner to 'member' or similar
        TeamMember.objects.filter(user=self.owner, team=self).update(role='member')
        # Logic to transfer ownership (e.g., update team owner field)
        # Assuming there's an 'owner' field in the Team model
        self.owner = new_owner
        self.save()
        # Also add the new owner as a member if not already a member
        if not self.members.filter(id=new_owner.id).exists():
            TeamMember.objects.get_or_create(user=new_owner, team=self, role='admin')

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Team.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_limit(self, feature_name):
        """
        Get the limit for a specific feature based on the team's plan.
        """
        if self.plan:
            return self.plan.get_feature(f"{feature_name}_limit")
        return None


class TeamMember(models.Model):
    ROLE_CHOICES = (
        ("admin", _("Admin")),
        ("member", _("Member")),
        ("viewer", _("Viewer")),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="team_members",
        verbose_name=_("User"),
        help_text=_("The user who is a member of the team."),
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="team_membership",
        verbose_name=_("Team"),
        help_text=_("The team to which the user belongs."),
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ("admin", _("Admin")),
            ("member", _("Member")),
            ("viewer", _("Viewer")),
        ],
        default="member",
        verbose_name=_("Role"),
        help_text=_("The role of the user in the team."),
    )

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"

    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        unique_together = ("user", "team")

class TeamInvitation(models.Model):
    email = models.EmailField(
        verbose_name=_("Email"),
        help_text=_("The email address of the user being invited."),
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name=_("Team"),
        help_text=_("The team to which the user is being invited."),
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
        verbose_name=_("Invited By"),
        help_text=_("The user who sent the invitation."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the invitation was created."),
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name=_("Accepted"),
        help_text=_("Indicates whether the invitation has been accepted."),
    )

    def __str__(self):
        return f"Invitation to {self.email} for {self.team.name}"
    
    class Meta:
        verbose_name = _("Team Invitation")
        verbose_name_plural = _("Team Invitations")
        unique_together = ("email", "team")

    def accept_invitation(self, user):
        """
        Accept the invitation and add the user to the team.
        """
        if not self.accepted:
            self.team.members.create(user=user, role="member")
            self.accepted = True
            self.save()
            return True
        return False