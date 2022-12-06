from django import template
from ..models import QrCode

register = template.Library()


@register.simple_tag
def hint(qr, team):
    return qr.hint(team)
