#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0.0
#   v 1.0.1 +image_original_url

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.exceptions import InvalidImageFormatError, EasyThumbnailsError
from common.functions import get_upload_path


class AbstractImage(models.Model, ):
    '''
Абстрактный класс для создания изображений
необходимо задать:
image_folder - для указания места хранения
imaged_prefix - для указания префикса размера в настройках
    '''

    class Meta:
        abstract = True
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    imaged_image_folder = 'images'
    imaged_prefix = None

    def _get_thumbnail_upload_path(self, filename):
        return get_upload_path(self.imaged_image_folder, filename)

    image = ThumbnailerImageField(
        null=True,
        blank=True,
        verbose_name=_('Image'),
        upload_to=_get_thumbnail_upload_path,
    )

    def image_tag(self):
        if (self.image):
            try:
                thumb_url = get_thumbnailer(self.image.name)['admin'].url
                return  mark_safe('<img src="%s" />' % thumb_url)
            except InvalidImageFormatError as e:
                return ''
            except EasyThumbnailsError as e:
                return ''
        return None
    image_tag.short_description = 'Image preview'
    image_tag.allow_tags = True

    def image_big_url(self):
        if (self.image):
            return get_thumbnailer(self.image.name)[self.imaged_prefix+'.big'].url
        return None

    def image_small_url(self):
        if (self.image):
            return get_thumbnailer(self.image.name)[self.imaged_prefix+'.small'].url
        return None

    def image_tiny_url(self):
        if (self.image):
            return get_thumbnailer(self.image.name)[self.imaged_prefix+'.tiny'].url
        return None

    def image_thumb_url(self):
        if (self.image):
            return get_thumbnailer(self.image.name)[self.imaged_prefix+'.thumb'].url
        return None

    def image_original_url(self):
        if (self.image):
            return self.image.url
        return None
