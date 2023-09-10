from django import template

register = template.Library()


@register.simple_tag
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None
