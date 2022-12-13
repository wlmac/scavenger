from django import template

register = template.Library()


@register.simple_tag
def hint(qr, team):
    return qr.hint(team)
