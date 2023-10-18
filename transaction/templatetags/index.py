from django import template
from datetime import datetime, timedelta

register = template.Library()


@register.simple_tag
def get_date(minutes):
    start = datetime.strptime('06:00', '%H:%M')
    end = start + timedelta(minutes=int(minutes))

    return str(start.strftime("%H:%M")) + ' - ' + str(end.strftime("%H:%M"))


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def divide(item, i):
    return item/i
