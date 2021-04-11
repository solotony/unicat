from django.db import models
from django.utils.translation import ugettext_lazy as _

class MeasureUnit(models.Model):
    """
    Measure Unit
    """

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Measure Unit')
        verbose_name_plural = _('Measure Units')

    name = models.CharField(
        max_length=200,
        verbose_name=_('name')
    )

    icecat_id = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('icecat id'),
    )

    def __str__(self):
        if self.name == 'None':
            return ''
        if self.name is None:
            return ''
        return self.name
