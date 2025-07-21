from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from apps.forms.models import Form, FormStyle
from apps.analytics.models import PageView, VisitorSession
from apps.analytics.models import Site
from django.conf import settings


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
                domain=settings.SITE_URL,
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
