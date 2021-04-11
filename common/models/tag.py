#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0.1


from django.db import models
from math import log2
from transliterate import slugify
from django.urls import reverse
from random import  randint
from django.utils.translation import gettext_lazy as _

class AbstractTag(models.Model):

    class Meta:
        abstract = True
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ('name',)

    route_name = None

    name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        max_length=60,
        verbose_name=_('Verbose name')
    )

    slug = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('Slug'),
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name, 'ru')
            self.slug = slug
            while True:
                qs = self.__class__.objects.filter(slug=self.slug)
                if self.id:
                    qs.exclude(id=self.id)
                if qs.first():
                    self.slug = slug + str(randint(0,1000000000))
                    continue
                break
        super(AbstractTag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.route_name:
            return reverse(self.route_name, args=(self.slug,))
        else:
            return None

    def __str__(self):
        return self.name



#   v 1.0.1 - добавлены переводы