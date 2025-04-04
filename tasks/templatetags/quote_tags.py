# your_app/templatetags/quote_tags.py
from django import template
from root.quotes_storage import get_random_quote

register = template.Library()

@register.simple_tag
def random_stoic_quote():
    return get_random_quote()