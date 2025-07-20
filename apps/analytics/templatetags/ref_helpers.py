from urllib.parse import urlparse
from django import template

register = template.Library()

@register.filter
def domain(url):
    try:
        return urlparse(url).netloc
    except:
        return url

@register.filter
def favicon(url):
    try:
        domain = urlparse(url).netloc
        return f"https://www.google.com/s2/favicons?domain={domain}"
    except:
        return ""
