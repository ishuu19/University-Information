from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter
@stringfilter
def split(value, arg):
    """Split a string into a list on the given delimiter."""
    return [x.strip() for x in value.split(arg)]

@register.filter
@stringfilter
def trim(value):
    """Remove leading and trailing whitespace."""
    return value.strip()

@register.filter
def split_after_number(value):
    if not value:
        return []
    # Find all patterns of text followed by a number
    pattern = r'([A-Za-z\s]+:\s*\d+\.?\d*)'
    matches = re.findall(pattern, value)
    # Clean up each match
    result = [match.strip() for match in matches]
    return result

@register.filter
def split_numbered_list(value):
    if not value:
        return []
    # Find all numbered items with their numbers
    pattern = r'(\d+)\.\s*([^0-9]+)'
    matches = re.findall(pattern, value)
    # Format each match with its number
    result = [f"{num}. {item.strip()}" for num, item in matches]
    return result

@register.filter
def split_test_scores(value):
    if not value:
        return []
    # Split by "GRE" and clean up
    parts = re.split(r'(?=GRE)', value)
    # Clean up each part
    result = [part.strip() for part in parts if part.strip()]
    return result 