from django.conf import settings

def site_context_processor(request):
    """
    Context processor to add site-related information to the context.
    """
    return {
        "PINGFOX_SITE_ID": settings.PINGFOX_SITE_ID,
        "PINGFOX_JS_SRC_URL": settings.PINGFOX_JS_SRC_URL,
        "PINGFOX_VERIFICATION_TOKEN": settings.PINGFOX_VERIFICATION_TOKEN,
    }