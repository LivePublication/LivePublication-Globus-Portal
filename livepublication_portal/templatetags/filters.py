from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.filter(name='split_username')
def split_username(value):
    return value.split('@')[0] if value and '@' in value else value

@register.simple_tag(takes_context=True, name='nav_active')
def nav_active(context, view_name):
    try:
        pattern = reverse(view_name)
        print(pattern)
    except NoReverseMatch:
        pattern = view_name
    path = context['request'].path
    return 'active' if path == pattern else ''