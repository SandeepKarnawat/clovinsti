from django import template
register = template.Library()

@register.simple_tag 
def define(val=None):
  return val

@register.simple_tag 
def percentage(part, whole):
    try:
        return "%d%%" % (float(part) / whole * 100)
    except (ValueError, ZeroDivisionError):
        return ""