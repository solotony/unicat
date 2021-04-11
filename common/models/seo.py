#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0

from django.db import models
from django.utils.translation import gettext_lazy as _

class SeoMixin(models.Model):
    '''
    Миксин добавляет поля для SEO - seo_title, seo_description
    для настройки используются поля seo_title_base и seo_description_base
    при отсутствубщих seo_title и seo_description возвращается значение полей,
    указываемых переменными seo_title_base и seo_description_base соответствнно
    '''

    class Meta:
        abstract = True

    seo_title_base = None
    seo_description_base = None

    _seo_title = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        verbose_name=_('SEO title')
    )

    _seo_description = models.CharField(
        null=True,
        blank=True,
        max_length=400,
        verbose_name=_('SEO description')
    )

    def get_seo_title(self):
        if self._seo_title:
            return self._seo_title
        if self.seo_title_base:
            return getattr(self, self.seo_title_base)

    def set_seo_title(self, value):
        self._seo_title = value

    seo_title = property(
        get_seo_title,
        set_seo_title
    )

    def get_seo_description(self):
        if self._seo_description:
            return self._seo_description
        if self.seo_description_base:
            return getattr(self, self.seo_description_base)

    def set_seo_description(self, value):
        self._seo_description = value

    seo_description = property(
        get_seo_description,
        set_seo_description
    )

