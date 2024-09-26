from django import template
import re

register = template.Library()

@register.filter
def regex_findall(value, arg):
    return re.findall(arg, value)