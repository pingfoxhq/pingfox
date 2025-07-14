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
        help_text=_("The price of the billing plan in the INR (₹)."),
    )
    description = models.TextField(
        verbose_name=_("Plan Description"),
        blank=True,
        help_text=_("A description of this plan."),
    )

    # Display and state
    is_active = models.BooleanField(
        verbose_name=_("Is Active"),
        default=True,
        help_text=_("Is the plan currently visible and available for users to select?"),
    )
    visible = models.BooleanField(
        verbose_name=_("Visible"),
        default=True,
        help_text=_("Is the plan visible to users?"),
    )
    highlighted = models.BooleanField(
        verbose_name=_("Highlighted"),
        default=False,
        help_text=_("Whether this plan should be highlighted in the UI."),
    )
    ranking = models.PositiveIntegerField(
        verbose_name=_("Ranking"),
        default=0,
        help_text=_("The ranking of the plan for display purposes."),
    )

    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("The date and time when the plan was created."),
    )

    def __str__(self):
        return self.name
    
    def get_feature(self, key, default=None):
        """
        Get the value of a specific feature by its key.
        Returns the default value if the feature does not exist.
        """
        feature = self.features.filter(key=key).first()
        return feature.value if feature else default


class PlanFeature(models.Model):
    """
    Represents a feature of a billing plan.
    """

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("Plan"),
        help_text=_("The billing plan this feature belongs to."),
    )
    key = models.CharField(
        max_length=100,
        verbose_name=_("Feature Key"),
        help_text=_("A unique key for the feature, used for identification."),
    )
    value = models.CharField(
        max_length=255,
        verbose_name=_("Feature Value"),
        help_text=_("The value of the feature, which can be a string or JSON."),
    )

    def __str__(self):
        return f"{self.plan.slug} → {self.key} = {self.value}"

    class Meta:
        unique_together = ("plan", "key")
