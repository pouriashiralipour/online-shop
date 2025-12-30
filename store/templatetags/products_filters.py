from django import template

register = template.Library()


@register.filter
def top_only(products):
    return [p for p in products if p.top_product]
