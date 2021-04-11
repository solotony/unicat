#    ____            _           _____
#   / ___|    ___   | |   ___   |_   _|   ___    _ __    _   _
#   \___ \   / _ \  | |  / _ \    | |    / _ \  | '_ \  | | | |
#    ___) | | (_) | | | | (_) |   | |   | (_) | | | | | | |_| |
#   |____/   \___/  |_|  \___/    |_|    \___/  |_| |_|  \__, |
#   1998-2020 (c) SoloTony.com                           |___/
#   v 1.0.1

from django.db import models
from django.utils.translation import gettext_lazy as _

class TimestampsMixin(models.Model):
    '''
    Миксин добавляет поля created_at и updated_at
    '''

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        null=False,
        blank=False,
        editable=False,
        db_index=False,
        verbose_name=_('Creation time'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        null=False,
        blank=False,
        editable=False,
        db_index=False,
        verbose_name=_('Modification time'),
        auto_now=True
    )


class TimestampsMixinIndexed(models.Model):
    '''
    Миксин добавляет поля created_at и updated_at
    Для полей created_at и updated_at создаются индексы
    '''

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        null=False,
        blank=False,
        editable=False,
        db_index=True,
        verbose_name=_('Creation time'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        null=False,
        blank=False,
        editable=False,
        db_index=True,
        verbose_name=_('Modification time'),
        auto_now=True
    )

#   v 1.0.1 - добавлены переводы