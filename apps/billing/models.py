from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import secrets
from apps.accounts.models import User, Team

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
        default=0.00,
        blank=True,
        null=True,
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

    is_base_plan = models.BooleanField(
        verbose_name=_("Is Base Plan"),
        default=False,
        help_text=_("Indicates if this is the base plan that all teams start with."),
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
    
    @property
    def is_pro(self):
        """
        Check if the plan is a Pro plan.
        """
        return self.get_feature("is_pro", False) == "true"


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


    def save(self, *args, **kwargs):
        """
        Override save to ensure that the feature key is unique within the plan.
        """
        if not self.key:
            raise ValueError("Feature key cannot be empty.")
        super().save(*args, **kwargs)


def generate_redeem_code():
    """
    Generate a unique redeem code.
    The code is a random alphanumeric string of length 10.
    """
    return secrets.token_urlsafe(10)

class RedeemCode(models.Model):
    """
    Represents a redeem code for a billing plan.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Redeem Code"),
        help_text=_("The unique code that can be redeemed for a billing plan."),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A description of what the redeem code offers."),
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name="redeem_codes",
        verbose_name=_("Plan"),
        help_text=_("The billing plan that this redeem code applies to."),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Indicates if the redeem code is currently active."),
    )
    usage_limit = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Usage Limit"),
        help_text=_("The maximum number of times this redeem code can be used."),
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Used Count"),
        help_text=_("The number of times this redeem code has been used."),
    )
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Valid From"),
        help_text=_("The date and time from which the redeem code is valid."),
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Valid Until"),
        help_text=_("The date and time until which the redeem code is valid."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when the redeem code was created."),
    )

    def __str__(self):
        return self.code
    
    def is_valid(self):
        """
        Check if the redeem code is valid based on its active status, usage limit,
        and validity period.
        """
        if not self.is_active:
            return False
        if self.used_count >= self.usage_limit:
            return False
        if self.valid_from and self.valid_from > timezone.now():
            return False
        if self.valid_until and self.valid_until < timezone.now():
            return False
        return True
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure the redeem code is unique and generate a new code if not provided.
        """
        if not self.code:
            self.code = generate_redeem_code()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = _("Redeem Code")
        verbose_name_plural = _("Redeem Codes")
        ordering = ["-created_at"]
        unique_together = ("code", "plan")


class CodeRedemption(models.Model):
    """
    Represents a redemption of a redeem code.
    This model tracks which user redeemed which code and when and for which team.
    """
    redeem_code = models.ForeignKey(
        RedeemCode,
        on_delete=models.CASCADE,
        related_name="redemptions",
        verbose_name=_("Redeem Code"),
        help_text=_("The redeem code that was redeemed."),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="code_redemptions",
        verbose_name=_("User"),
        help_text=_("The user who redeemed the code."),
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="code_redemptions",
        verbose_name=_("Team"),
        help_text=_("The team for which the code was redeemed."),
    )
    redeemed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Redeemed At"),
        help_text=_("The date and time when the code was redeemed."),
    )

    def __str__(self):
        return f"{self.user.username} redeemed {self.redeem_code.code} for {self.team.name}"
    
    class Meta:
        verbose_name = _("Code Redemption")
        verbose_name_plural = _("Code Redemptions")
        ordering = ["-redeemed_at"]
        unique_together = ("redeem_code", "user", "team")
