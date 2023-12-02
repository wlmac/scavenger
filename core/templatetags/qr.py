import re

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


@register.simple_tag
def ending_block(hunt):
    pattern = r"{{(.*?)}}"
    match = re.search(pattern, hunt.ending_text)

    if match:
        ending_text = match.group(1).strip()
        return format_html(
            hunt.ending_text.replace(match.group(0), '<a href="{}">{}</a>'.format(hunt.ending_form, ending_text)))
    return hunt.ending_text
