#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0

import os
from transliterate import slugify
from time import strftime
import re
import logging

logger_hashtags = logging.getLogger('hashtags')

def get_upload_path(folder:str, filename:str)->str:
    '''
        Возвращает путь для сохранения объекта (файла, изображения)
    '''
    file_name, file_extension = os.path.splitext(filename)
    return os.path.join('media', folder, strftime("%Y/%m/%d/"), slugify(file_name, 'ru') + file_extension)

re_hashtag = re.compile(r'##([a-z0-9#_.-]+)##', flags=re.IGNORECASE)

def get_client_ip(request):

    ip_address = '127.0.0.1'

    if request.META.get('REMOTE_ADDR'):
        ip_address = request.META.get('REMOTE_ADDR')
    if request.META.get('HTTP_CLIENT_IP'):
        ip_address = request.META.get('HTTP_CLIENT_IP')
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        for ip in str(request.META.get('HTTP_X_FORWARDED_FOR')).split(','):
            ip_address = ip.strip()
    if request.META.get('HTTP_X_FORWARDED'):
        ip_address = request.META.get('HTTP_X_FORWARDED')
    elif request.META.get('HTTP_X_CLUSTER_CLIENT_IP'):
        ip_address = request.META.get('HTTP_X_CLUSTER_CLIENT_IP')
    elif request.META.get('HTTP_FORWARDED_FOR'):
        ip_address = request.META.get('HTTP_FORWARDED_FOR')
    elif request.META.get('HTTP_FORWARDED_FOR'):
        ip_address = request.META.get('HTTP_FORWARDED_FOR')
    elif request.META.get('HTTP_X_REAL_IP'):
        ip_address = request.META.get('HTTP_X_REAL_IP')

    return ip_address

