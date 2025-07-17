from django.db import models
from django.utils.translation import gettext_lazy as _


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