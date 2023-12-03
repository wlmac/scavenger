from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def hint(qr, team):
    return qr.hint(team)


@register.simple_tag
def join_url(code):
    return format_html("%s%s" % (reverse("join"), f"?code={code}"))
