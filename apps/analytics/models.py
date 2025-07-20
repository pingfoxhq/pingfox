from django.db import models
from django.utils.translation import gettext_lazy as _

import secrets
from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.accounts.models import Team, User

def generate_site_id():
    return secrets.token_urlsafe(8)[:11]

def generate_verification_token():
    return secrets.token_urlsafe(256)

def verification_file_path():
        """
        Returns the file path for the verification token.
        This should be placed at ~/.well-known/pingfox-verification.txt.
        """
        return ".well-known/pingfox-verification.txt"

class Site(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="sites",
        verbose_name=_("Team"),
        help_text=_("The team that owns this site."),
    )
         
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sites",
        verbose_name=_("Owner"),
        help_text=_("The user who made this site."),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("A human-readable label for this site (e.g. 'Personal Blog')."),
    )
    domain = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Domain"),
        help_text=_(
            "The domain name for this site (e.g. 'example.com' - no protocol)."
        ),
    )
    url = models.URLField(
        max_length=255,
        verbose_name=_("URL"),
        help_text=_("The full URL for this site (e.g. 'https://example.com')."),
    )
    site_id = models.CharField(
        max_length=24,
        unique=True,
        default=generate_site_id,
        verbose_name=_("Site ID"),
        help_text=_(
            "A unique identifier for this site, used in URLs and API calls and for serving the JS tracking script."
        ),
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Is Verified"),
        help_text=_("Indicates whether the site has been verified by the user."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_(
            "Indicates whether the site is currently active and should be tracked."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the site was created."),
    )
    pageview_limit_override = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Pageview Limit Override"),
        help_text=_(
            "An optional override for the site's pageview limit, if applicable."
        ),
    )
    timezone = models.CharField(
        max_length=50,
        default="Asia/Kolkata",
        verbose_name=_("Timezone"),
        help_text=_("The timezone for this site, used for date and time display."),
    )
    verification_token = models.CharField(
        max_length=256,
        unique=True,
        default=generate_verification_token,
        verbose_name=_("Verification Token"),
        help_text=_(
            f"A unique token used to verify ownership of the site. Place this in a file at the root of your domain as ~/{verification_file_path()}. "
        ),
    )
    homepage_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Homepage Title"),
        help_text=_("The title to display on the homepage of this site."),
    )
    favicon_url = models.URLField(
        blank=True,
        verbose_name=_("Favicon URL"),
        help_text=_("The URL of the favicon to use for this site."),
    )

    last_indexed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Indexed"),
        help_text=_("The date and time when the site was last indexed for content."),
    )
    # form = models.ForeignKey(
    #     Form,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="sites",
    #     verbose_name=_("Form"),
    #     help_text=_("The form associated with this site, if any."),
    # )
         

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.domain})"


class VisitorSession(models.Model):
    """
    Model to represent a unique visitor session to the site.
    It is based on the pf_id which is generated at the client side.
    """
    pf_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("PF ID"),
        help_text=_("Unique identifier for the visitor, generated at the client side.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("Timestamp when the visitor session was created.")
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Seen"),
        help_text=_("Timestamp when the visitor was last seen.")
    )
    user_agent = models.CharField(
        max_length=512,
        verbose_name=_("User Agent"),
        help_text=_("User agent string of the visitor's browser.")
    )
    def __str__(self):
        return f"Visitor {self.pf_id} - Last seen at {self.last_seen.isoformat()}"


class PageView(models.Model):
    """
    Model to track page views on the site.
    """
    visitor = models.ForeignKey(
        VisitorSession,
        on_delete=models.CASCADE,
        related_name="page_views",
        verbose_name=_("Visitor"),
        help_text=_("The visitor session associated with this page view.")
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="page_views",
        verbose_name=_("Site"),
        help_text=_("The site where the page view occurred.")
    )
    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("The URL of the page that was viewed.")
    )
    referrer = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Referrer"),
        help_text=_("The URL of the page that referred the visitor to this page.")
    )
    screen_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Screen Width"),
        help_text=_("The width of the visitor's screen in pixels.")
    )
    screen_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Screen Height"),
        help_text=_("The height of the visitor's screen in pixels.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Timestamp"),
        help_text=_("The timestamp when the page view occurred.")
    )

    def __str__(self):
        return f"{self.url} at {self.timestamp.isoformat()}"