from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from django.utils import timezone
from django.utils.text import slugify
import secrets

User = get_user_model()


def generate_activation_code():
    """
    Generate a random 6-digit activation code.
    """
    while True:
        code = secrets.token_hex(3).upper()
        if not UserActivation.objects.filter(activation_code=code).exists():
            return code


def generate_activation_code_expiration():
    """
    Generates a default expiration date for activation codes.

    Returns:
        datetime: A datetime object set to 24 hours from now.
    """
    return timezone.now() + timezone.timedelta(days=1)


def generate_team_slug(name):
    """
    Generate a unique slug for a team based on its name.
    If the slug already exists, append a number to make it unique.

    Args:
        name (str): The name of the team.

    Returns:
        str: A unique slug for the team.
    """
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while Team.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class UserProfile(models.Model):
    """
    User Profile model to store additional user information.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile",
        verbose_name=_("User Profile"),
        help_text=_("The user associated with this profile."),
    )
    avatar = ResizedImageField(
        upload_to="uploads/avatars/",
        size=[200, 200],
        crop=["middle", "center"],
        quality=90,
        verbose_name=_("Avatar"),
        null=True,
        blank=True,
        help_text=_("User's profile picture, resized to 200x200 pixels."),
        default="defaults/avatar.png",
    )

    def __str__(self):
        """
        Returns a string representation of the user profile.
        """
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        """
        Override save method to set default avatar if not provided.
        """
        if not self.avatar or self.avatar.name.startswith("defaults/"):
            self.avatar = "defaults/avatar.png"
        super().save(*args, **kwargs)

    def teams(self):
        """
        Returns a list of teams the user is a member of.
        """
        return self.user.team_members.all()


class UserActivation(models.Model):
    """
    User Activation model to manage user account activation.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="activation",
        verbose_name=_("User Activation"),
        help_text=_("The user associated with this activation."),
    )
    activation_code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_activation_code,
        verbose_name=_("Activation Code"),
        help_text=_("A unique code for activating the user's account."),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("Is Active"),
        help_text=_("Indicates whether the user's account is active."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the activation was created."),
    )
    expiration_date = models.DateTimeField(
        default=generate_activation_code_expiration,
        verbose_name=_("Expiration Date"),
        help_text=_("The date and time when the activation code expires."),
    )

    def __str__(self):
        """
        Returns a string representation of the activation.
        """
        return f"Activation for {self.user.username}"

    def is_expired(self):
        """
        Check if the activation code is expired.
        """
        return timezone.now() > self.expiration_date

    def activate(self):
        """
        Activate the user's account.
        """
        if not self.is_active and not self.is_expired():
            self.user.is_active = True
            self.user.save()
            self.is_active = True
            self.save()
            return True
        return False

    def regenerate_activation_code(self):
        """
        Regenerate the activation code.
        """
        self.activation_code = generate_activation_code()
        self.expiration_date = generate_activation_code_expiration()
        self.save()

    def save(self, *args, **kwargs):
        """
        Override save method to ensure activation code and expiration date are set.
        """
        if not self.activation_code:
            self.activation_code = generate_activation_code()
        if not self.expiration_date:
            self.expiration_date = generate_activation_code_expiration()
        super().save(*args, **kwargs)


class Team(models.Model):
    """Team model to manage teams and their members."""

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
        "billing.Plan",
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
        through="TeamMember",
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
        """
        Returns a string representation of the team.
        """
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
        """
        Check if the limit for a specific resource type is exceeded.
        Args:
            resource_type (str): The type of resource to check (e.g., 'forms', 'sites').
        Returns:
            bool: True if the limit is exceeded, False otherwise.
        """
        if resource_type == "forms":
            max_allowed = int(self.feature_limit("forms_limit")) or 3
            current_count = self.forms.count()
            return max_allowed is not None and current_count >= max_allowed
        elif resource_type == "sites":
            max_allowed = int(self.feature_limit("sites_limit")) or 1
            current_count = self.sites.filter(form=None).count()
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
        TeamMember.objects.filter(user=self.owner, team=self).update(role="member")
        # Logic to transfer ownership (e.g., update team owner field)
        # Assuming there's an 'owner' field in the Team model
        self.owner = new_owner
        self.save()
        # Also add the new owner as a member if not already a member
        if not self.members.filter(id=new_owner.id).exists():
            TeamMember.objects.get_or_create(user=new_owner, team=self, role="admin")

    class Meta:
        """
        Meta options for Team model.
        """

        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        ordering = ["name"]

    def get_limit(self, feature_name):
        """
        Get the limit for a specific feature based on the team's plan.
        """
        if self.plan:
            return self.plan.get_feature(f"{feature_name}_limit")
        return None

    def save(self, *args, **kwargs):
        """
        Override save method to ensure slug is unique.
        """
        if not self.slug:
            self.slug = generate_team_slug(self.name)
        super().save(*args, **kwargs)


class TeamMember(models.Model):
    """
    Model representing a member of a team with a specific role.
    """

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
        """
        Returns a string representation of the team member.
        """
        return f"{self.user.username} - {self.team.name} ({self.role})"

    class Meta:
        """
        Meta options for TeamMember model.
        """

        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        unique_together = ("user", "team")


class TeamInvitation(models.Model):
    """
    Model representing an invitation to join a team.
    """

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
        """
        Returns a string representation of the invitation.
        """
        return f"Invitation to {self.email} for {self.team.name}"

    class Meta:
        """
        Meta options for TeamInvitation model.
        """

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
