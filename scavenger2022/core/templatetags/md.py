from django import template
from django.utils.html import mark_safe
import mistune as mistune_

register = template.Library()


@register.filter
def mistune(value):
    return mark_safe(mistune_.html(value))
