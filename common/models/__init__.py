from django.db import models
import os
from transliterate import slugify
from time import strftime

def get_upload_path(folder:str, filename:str) -> str:
    '''
    **DEPRECATED**
    надо исползовать functions.get_upload_path
    '''
    file_name, file_extension = os.path.splitext(filename)
    return os.path.join('media', folder, strftime("%Y/%m/%d/"), slugify(file_name, 'ru') + file_extension)

class TextFormats():

    TEXT_LINEBREAKS = 0
    TEXT_RAW_HTML = 1
    TEXT_MARKDOWN = 2
    TEXT_CODE = 3

    TEXT_TYPES=(
        (TEXT_LINEBREAKS, 'переводы строк и ссылки'),
        (TEXT_RAW_HTML, 'HTML'),
        (TEXT_MARKDOWN, 'MarkDown'),
        (TEXT_CODE, 'код (моноширинный текст)'),
    )
