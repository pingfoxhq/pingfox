from django.db import models
from django.utils.translation import gettext_lazy as _


class Plan(models.Model):
    """
    Represents a billing plan for users.
    """

    name = models.CharField(
        verbose_name=_("Plan Name"),
        max_length=100,
        unique=True,
        help_text=_("The name of the billing plan."),
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name=_("Plan Slug"),
        unique=True,
        help_text=_("A URL-friendly identifier for the billing plan."),
    )
    price = models.DecimalField(
        verbose_name=_("Plan Price"),
        max_digits=10,
        decimal_places=2,
        help_text=_(
            "The price of the billing plan in the smallest currency unit (e.g., cents)."
        ),
    )
    features = models.TextField(
        verbose_name=_("Plan Features"),
        blank=True,
        help_text=_("A description of the features included in this plan."),
    )
    is_pro = models.BooleanField(
        verbose_name=_("Is Pro Plan"),
        default=False,
        help_text=_("Is this plan a Pro plan?"),
    )

    requires_expiry = models.BooleanField(
        verbose_name=_("Requires Expiry Date"),
        default=False,
        help_text=_("Does this plan require an expiry date?"),
    )
    pageview_limit = models.PositiveIntegerField(
        verbose_name=_("Pageview Limit"),
        default=0,
        help_text=_(
            "The maximum number of pageviews allowed per month. 0 means unlimited."
        ),
    )
    script_bagde = models.BooleanField(
        verbose_name=_("Script Badge"),
        default=False,
        help_text=_("Whether the plan includes a script badge."),
    )
    is_active = models.BooleanField(
        verbose_name=_("Is Active"),
        default=True,
        help_text=_("Is the plan currently visible and available for users to select?"),
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("The date and time when the plan was created."),
    )

    def __str__(self):
        return self.name
