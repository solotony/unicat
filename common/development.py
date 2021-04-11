#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0
#
'''
Development tools:
devprt - print only when DEVELOPE setting is True
'''

import functools
from django.conf import settings

def devprt(mode, *args, **kwargs):
    '''print only when DEVELOPE setting is True'''
    if settings.DEVELOPE and mode in settings.DEBUGS:
        print(*args, **kwargs)

def monitor_results(func):
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        if settings.DEVELOPE and 'TRACE' in settings.DEBUGS:
            params = str(func_args) + str(func_kwargs)
            print(' -- ' + func.__name__, "(" + params + ")")
        retval = func(*func_args, **func_kwargs)
        if settings.DEVELOPE and 'TRACE' in settings.DEBUGS:
            print(' -- ' + func.__name__ + "(" + params + ") => " + repr(retval))
        return retval
    return wrapper
