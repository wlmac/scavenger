import mistune as mistune_
from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def mistune(value):
    return mark_safe(mistune_.html(str(value)))
