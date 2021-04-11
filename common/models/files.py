#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0.0

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.exceptions import InvalidImageFormatError, EasyThumbnailsError
from common.functions import get_upload_path


class AbstractFile(models.Model, ):
    '''
Абстрактный класс для создания списка файлов
необходимо задать:
files_folder - для указания места хранения
    '''

    class Meta:
        abstract = True
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    files_folder = 'files'

    def _get_thumbnail_upload_path(self, filename):
        return get_upload_path(self.files_folder, filename)

    file = models.FileField(
        null=True,
        blank=True,
        verbose_name=_('File'),
        upload_to=_get_thumbnail_upload_path,
    )

    def file_url(self):
        if (self.file):
            return self.file.url
        return None
