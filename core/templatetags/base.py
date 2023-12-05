from django import template

register = template.Library()


@register.filter
def format_time(d):
    return {0: "", 1: "1 day, "}.get(
        d.days, f"{d.days} days, "
    ) + f"{int(d.seconds//3600):02}:{int(d.seconds//60%60):02}:{int(d.seconds%60):02}"
