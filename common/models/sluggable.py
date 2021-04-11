#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse
from transliterate import slugify
from random import  randint
from time import time

class SluggableMixin(models.Model):
    '''
    миксин добавляет "slug"
    необходимо задать:
    slug_base - поле используемое для автоматического вычисления slug
    route - имя роута
    '''

    class Meta:
        abstract = True

    slug_base = None
    route = None

    slug = models.CharField(
        null=True,
        blank=True,
        unique=True,
        max_length=200,
        verbose_name=_('Slug')
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            if self and self.slug_base:
                slug = slugify(getattr(self, self.slug_base), 'ru')[:190]
                self.slug = slug
                while True:
                    qs = self.__class__.objects.filter(slug=self.slug)
                    if self.id:
                        qs.exclude(id=self.id)
                    if qs.exists():
                        self.slug = slug + '_' + str(randint(0,999999999))
                        continue
                    break
            else:
                self.slug = str(time()) + '_' + str(randint(0, 999999999))
        super().save(*args, **kwargs)

    page_path = property(
        lambda self:reverse(self.route, self.slug)
    )

