#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.1

from django import template
import re

register = template.Library()

re_not_clean_phone_digits = re.compile("[^0-9+]")

@register.filter()
def clean_phone_number(value):
    """
    prepare clean phone numer to use in href="tel: ... "
    """
    if not value:
        return ''
    value = str(value)
    return re_not_clean_phone_digits.sub('', value)


@register.simple_tag
def define(value=None):
    return str(value)


# v 1.1
# - add define