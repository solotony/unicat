from django.db import models
from django.utils.translation import ugettext_lazy as _
from catalog.models.eav import Attribute, AttributeChoice, AttributeValue


class SlotAttribute(Attribute):

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Slot attribute')
        verbose_name_plural = _('Slot attributes')


class SlotAttributeChoice(AttributeChoice):

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Slot attribute choice')
        verbose_name_plural = _('Slot attribute choices')

    attribute = models.ForeignKey(
        SlotAttribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name=_('attribute')
    )


class Slot(models.Model):

    class Meta:
        app_label = 'catalog'
        verbose_name = _('Slot')
        verbose_name_plural = _('Slots')

    name = models.CharField(
        max_length=200,
        verbose_name=_('name')
    )

    printstore_id = models.BigIntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('PrintStore id'),
    )

    order = models.IntegerField(
        verbose_name=_('sort order'),
        null=False,
        blank=False,
        default = 0
    )


class SlotAttributeValue(AttributeValue):

    class Meta:
        app_label = 'catalog'
        unique_together = (
            ('slot', 'attribute')
        )

    slot = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    attribute = models.ForeignKey(
        SlotAttribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

