#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0.3

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.fields import ThumbnailerImageField
from common.functions import get_upload_path
from easy_thumbnails.exceptions import InvalidImageFormatError, EasyThumbnailsError
import logging

logger = logging.getLogger()

class ThumbnailedMixin(models.Model):
    '''
Миксин добавляет поле image
необходимо задать:
thumbnaled_image_folder - для указания места хранения
thumbnaled_prefix - для указания префикса размера в настройках
    '''

    thumbnaled_image_folder = 'images'
    thumbnaled_prefix = None

    class Meta:
        abstract = True

    def _get_thumbnail_upload_path(self, filename):
        return get_upload_path(self.thumbnaled_image_folder, filename)

    image = ThumbnailerImageField(
        null=True,
        blank=True,
        verbose_name=_('Images'),
        upload_to=_get_thumbnail_upload_path,
    )

    def image_custom_tag_url(self, thumbnail_name):
        if (self.image):
            try:
                thumb_url = get_thumbnailer(self.image.name)[thumbnail_name].url
                return  mark_safe('<img src="%s" />' % thumb_url)
            except InvalidImageFormatError as e:
                logger.error('image_tag({}) : {}'.format(self.image.name, str(e)))
                return None
            except EasyThumbnailsError as e:
                logger.error('image_tag({}) : {}'.format(self.image.name, str(e)))
                return None
        return None

    def image_tag(self):
        return self.image_custom_tag_url('admin')
    image_tag.short_description = 'Image preview'
    image_tag.allow_tags = True

    def image_custom_url(self, thumbnail_name):
        if (self.image):
            try:
                return get_thumbnailer(self.image.name)[thumbnail_name].url
            except InvalidImageFormatError as e:
                logger.error('image_thumb_url({}) : {}'.format(self.image.name, str(e)))
                return None
            except EasyThumbnailsError as e:
                logger.error('image_thumb_url({}) : {}'.format(self.image.name, str(e)))
                return None
        return None


    def image_big_url(self):
        return self.image_custom_url(self.thumbnaled_prefix+'.big')

    def image_small_url(self):
        return self.image_custom_url(self.thumbnaled_prefix + '.small')

    def image_tiny_url(self):
        return self.image_custom_url(self.thumbnaled_prefix + '.tiny')

    def image_thumb_url(self):
        return self.image_custom_url(self.thumbnaled_prefix + '.thumb')


#   v 1.0.1 - добавлены переводы
#   v 1.0.2 - добавлена обработка ошибок
#   v 1.0.2.1 - исправлена ошибка thumbnaled_prefix
#   v 1.0.3 + image_custom_url