from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from apps.forms.models import Form, FormStyle, FormSubmission
from apps.analytics.models import PageView, VisitorSession
from apps.analytics.models import Site
from django.conf import settings
from apps.hooks.models import WebhookEvent
from apps.hooks.tasks import deliver_webhook

@receiver(post_save, sender=Form)
def create_form_analytics(sender, instance, created, **kwargs):
    if created:
        FormStyle.objects.get_or_create(form=instance)

        if instance.allow_analytics:
            # Create a default VisitorSession for the form
            site, created = Site.objects.get_or_create(
                team=instance.team,
                owner=instance.owner,
                name=f"{instance.name} [Analytics]",
                is_active=True,
                is_verified=True,
                domain=settings.SITE_URL or "localhost",
                url=f"{settings.SITE_URL}{instance.get_absolute_url()}",
                form=instance,
            )
            instance.site_id = site.site_id
            instance.save()


@receiver(pre_delete, sender=Form)
def delete_form_analytics(sender, instance, **kwargs):
    Site.objects.filter(
        url=f"{settings.SITE_URL}{instance.get_absolute_url()}"
    ).delete()


@receiver(post_save, sender=FormSubmission)
def create_form_submission_webhook(sender, instance, created, **kwargs):
    if created:
        if not instance.form.webhook_url or not instance.form.webhook_secret:
            return
        # Trigger a webhook event for the new form submission
        event = WebhookEvent.objects.create(
            type=WebhookEvent.FORM_SUBMITTED,
            team_id=instance.form.team_id,
            site_id=instance.form.site.site_id or None,
            data={
                "form_id": instance.form.id,
                "form_name": instance.form.name,
                "submission_id": instance.id,
                "submitted_at": instance.submitted_at.isoformat(),
                "fields": instance.cleaned_data,
            }
        )
        deliver_webhook.send(
            event.id,
            webhook_url=instance.form.webhook_url,
            secret=instance.form.webhook_secret
        )