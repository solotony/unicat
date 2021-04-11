from django import template

register = template.Library()

def sub_filter(value, arg):
    return value - arg

register.filter('sub', sub_filter)


@register.simple_tag(name='range')
def range_tag(start, end):
    return range(start, end)


@register.simple_tag(name='paginator')
def paginator_tag(current_page, num_pages):

    pages = []

    if current_page > 1:
        pages.append(('first', 1))

    for num in range(current_page-4, current_page):
        if num > 0:
            pages.append((num, num))

    pages.append(('this', current_page))

    for num in range(current_page+1, current_page+5):
        if num <= num_pages:
            pages.append((num, num))

    if current_page < num_pages:
        pages.append(('last', num_pages))

    return pages


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.update(kwargs)
    return query.urlencode()