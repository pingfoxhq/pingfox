from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import secrets
from django_resized import ResizedImageField
from colorfield.fields import ColorField
from apps.teams.models import Team
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from apps.analytics.models import VisitorSession

User = get_user_model()


def generate_auth_key(length=40):
    """
    Generates a secure, URL-safe authentication key.

    - Uses `secrets` for cryptographic randomness.
    - Default length is 40 characters (sufficiently secure for auth keys).
    - Characters are URL-safe (won't break in query strings or headers).
    """
    while True:
        key = secrets.token_urlsafe(length)[:length]
        if not Form.objects.filter(auth_key=key).exists():
            return key
        
def generate_slug():
    """
    Generates a unique slug for a form.
    
    - Uses `secrets` to ensure uniqueness.
    - Slugs are URL-safe and suitable for use in URLs.
    """
    while True:
        slug = secrets.token_urlsafe(6)
        if not Form.objects.filter(slug=slug).exists():
            return slug


class Form(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="forms",
        verbose_name=_("Team"),
        help_text=_("The team to which this form belongs."),
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="forms",
        verbose_name=_("Form Owner"),
        help_text=_("The user who owns the form."),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Form Name"),
        help_text=_("The name of the form."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        default=generate_slug,
        verbose_name=_("Slug"),
        help_text=_("A unique identifier for the form, used in URLs."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of the form."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the form was created."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Indicates whether the form is currently active."),
    )
    authentication_required = models.BooleanField(
        default=False,
        verbose_name=_("Authentication Required"),
        help_text=_(
            "Indicates whether users must be authenticated to submit this form."
        ),
    )
    auth_key = models.CharField(
        max_length=40,
        unique=True,
        default=generate_auth_key,
        verbose_name=_("Authentication Key"),
        help_text=_("A unique key required for authenticated form submissions."),
    )

    redirect_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Redirect URL"),
        help_text=_("URL to redirect users after form submission."),
    )

    allow_multiple_submissions = models.BooleanField(
        default=True,
        verbose_name=_("Allow Multiple Submissions"),
        help_text=_(
            "Indicates whether users can submit this form multiple times."
        ),
    )

    button_text = models.CharField(
        max_length=255,
        default=_("Submit"),
        verbose_name=_("Button Text"),
        help_text=_("The text displayed on the form submission button."),
    )

    # This field is used to track visitors who have interacted with the form
    # It can be used for analytics or to prevent spam submissions also for preventing multiple submissions
    visitors = models.ManyToManyField(
        VisitorSession,
        blank=True,
        related_name="forms",
        verbose_name=_("Visitors"),
        help_text=_("Visitors who have interacted with this form."),
    )

    is_locked = models.BooleanField(
        default=False,
        verbose_name=_("Is Locked"),
        help_text=_("Indicates whether the form is locked for editing."),
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Returns the absolute URL for the form.
        """
        return f"/f/{self.slug}/"

    class Meta:
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")
        ordering = ["-created_at"]
        unique_together = ("owner", "slug")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner"]),
        ]


    def save(self, *args, **kwargs):
        # Check if the owner is in the team
        if not self.owner in self.team.members.all():
            raise ValueError("Owner must be a member of the team.")
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Form.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        super().save(*args, **kwargs)



class FormStyle(models.Model):
    FONT_CHOICES = [
        ("system", "System Default"),
        ("inter", "Inter"),
        ("dyslexic", "OpenDyslexic"),
        ("serif", "Serif"),
        ("mono", "Monospace"),
        ("sans-serif", "Sans-Serif"),
    ]

    form = models.OneToOneField(
        Form,
        on_delete=models.CASCADE,
        related_name="style",
        verbose_name=_("Form"),
        help_text=_("The form to which this style belongs."),
    )
    background_color = ColorField(
        default="#ffffff",
        verbose_name=_("Background Color"),
        help_text=_("The background color of the form in hex format."),
    )
    text_color = ColorField(
        default="#000000",
        verbose_name=_("Text Color"),
        help_text=_(
            "The text color used in the form, such as for labels and instructions."
        ),
    )
    accent_color = ColorField(
        default="#f97316",
        verbose_name=_("Accent Color"),
        help_text=_("The accent color used for buttons and highlights in the form."),
    )
    button_color = ColorField(
        default="#f97316",
        verbose_name=_("Button Color"),
        help_text=_("The color of the form submission button."),
    )
    button_text_color = ColorField(
        default="#ffffff",
        verbose_name=_("Button Text Color"),
        help_text=_("The text color of the form submission button."),
    )

    font_family = models.CharField(
        max_length=100,
        default="Arial, sans-serif",
        verbose_name=_("Font Family"),
        choices=FONT_CHOICES,
        help_text=_("The font family used in the form."),
    )
    logo = ResizedImageField(
        upload_to="form_logos/",
        size=[300, 100],
        crop=["middle", "center"],
        quality=90,
        blank=True,
        null=True,
        verbose_name=_("Logo"),
        help_text=_("The logo image for the form."),
    )
    custom_css = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Custom CSS"),
        help_text=_("Custom CSS styles for the form."),
    )
    

    def __str__(self):
        return f"Style for {self.form.name}"

    class Meta:
        verbose_name = _("Form Style")
        verbose_name_plural = _("Form Styles")

    def get_font_family_display(self):
        """
        Returns a human-readable display of the font family.
        """
        return dict(self.FONT_CHOICES).get(self.font_family, self.font_family)

class FormField(models.Model):
    FIELD_TYPES = [
        ("text", _("Text")),
        ("email", _("Email")),
        ("number", _("Number")),
        ("date", _("Date")),
        ("checkbox", _("Checkbox")),
        ("select", _("Select")),
        ("radio", _("Radio")),
        ("textarea", _("Textarea")),
    ]

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="fields",
        verbose_name=_("Form"),
        help_text=_("The form to which this field belongs."),
    )
    label = models.CharField(
        max_length=1024,
        verbose_name=_("Field Label"),
        help_text=_("The label for the form field."),
    )
    field_type = models.CharField(
        max_length=50,
        choices=FIELD_TYPES,
        verbose_name=_("Field Type"),
        help_text=_("The type of the form field."),
    )
    name = models.SlugField(
        max_length=1024,
        verbose_name=_("Field Name"),
        help_text=_("A unique identifier for the field, used in form submissions."),
    )
    placeholder = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name=_("Placeholder"),
        help_text=_("Placeholder text for the field."),
    )
    required = models.BooleanField(
        default=False,
        verbose_name=_("Is Required"),
        help_text=_("Indicates whether this field is required."),
    )
    readonly = models.BooleanField(
        default=False,
        verbose_name=_("Is Readonly"),
        help_text=_("Indicates whether this field is readonly."),
    )
    hidden = models.BooleanField(
        default=False,
        verbose_name=_("Is Hidden"),
        help_text=_("Indicates whether this field is hidden from the user."),
    )
    disabled = models.BooleanField(
        default=False,
        verbose_name=_("Is Disabled"),
        help_text=_("Indicates whether this field is disabled."),
    )
    choices = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name=_("Choices"),
        help_text=_("Comma-separated list of choices (for select only)."),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("The order of the field in the form."),
    )
    validation_regex = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name=_("Validation Regex"),
        help_text=_("Regular expression for validating the field input."),
    )
    help_text = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name=_("Help Text"),
        help_text=_("Additional information or instructions for the field."),
    )
    default_value = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Default Value"),
        help_text=_("The default value for the field, if applicable."),
    )

    def __str__(self):
        return f"{self.form.name} - {self.label}"

    class Meta:
        verbose_name = _("Form Field")
        verbose_name_plural = _("Form Fields")
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = slugify(self.label)
        super().save(*args, **kwargs)


class FormSubmission(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name=_("Form"),
        help_text=_("The form to which this submission belongs."),
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submitted At"),
        help_text=_("The date and time when the form was submitted."),
    )
    data = models.JSONField(
        verbose_name=_("Submission Data"),
        help_text=_("The data submitted in the form."),
    )

    def __str__(self):
        return f"Submission for {self.form.name} at {self.submitted_at}"

    class Meta:
        verbose_name = _("Form Submission")
        verbose_name_plural = _("Form Submissions")
        ordering = ["-submitted_at"]
