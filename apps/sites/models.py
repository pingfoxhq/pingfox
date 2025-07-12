import secrets
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models


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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sites",
        verbose_name=_("User"),
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

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.domain})"

    def js_url(self):
        """
        Returns the URL for the JavaScript tracking script for this site.
        """
        return f"/collect/{self.site_id}.js"


class PageView(models.Model):
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="pageviews",
        verbose_name=_("Site"),
    )
    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("The URL of the page that was viewed."),
    )
    referrer = models.URLField(
        blank=True,
        verbose_name=_("Referrer"),
        help_text=_("The URL of the page that referred the user to this page."),
    )
    user_agent = models.TextField(
        verbose_name=_("User Agent"),
        help_text=_("The user agent string of the browser making the request."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the page view was recorded."),
    )

    class Meta:
        verbose_name = _("Page View")
        verbose_name_plural = _("Page Views")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.site.name} - {self.url} ({self.created_at})"
