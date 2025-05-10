from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string into a list using the specified delimiter."""
    if value is None:
        return []
    return [x.strip() for x in value.split(delimiter)]

@register.filter
def intcomma_format(value):
    """Format a number with commas as thousand separators."""
    if value is None:
        return "N/A"
    try:
        return intcomma(float(value))
    except (ValueError, TypeError):
        return "N/A"

@register.filter
def safe_html(value):
    """Mark a string as safe HTML."""
    return mark_safe(value)

@register.filter
def intcomma(value):
    """Converts an integer to a string containing commas."""
    try:
        if value is None:
            return ''
        orig = str(value)
        new = orig
        if '.' in new:
            dec = new.split('.')[1]
            orig = new.split('.')[0]
            new = orig
        if len(new) <= 3:
            return orig
        else:
            parts = []
            while len(new) > 3:
                parts.append(new[-3:])
                new = new[:-3]
            parts.append(new)
            parts.reverse()
            return ','.join(parts)
    except (TypeError, ValueError):
        return value

@register.filter
def currency(value):
    """Format a number as currency."""
    try:
        if value is None:
            return 'Contact university'
        return f"${intcomma(floatformat(value, 2))}"
    except (TypeError, ValueError):
        return 'Contact university' 