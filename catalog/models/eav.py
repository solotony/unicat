from django.db import models
from django.utils.translation import ugettext_lazy as _
from transliterate import slugify

from catalog.models.units import MeasureUnit
from django.utils.html import mark_safe

class Attribute(models.Model):
    """
    base abstract EAV attribute
    """

    class Meta:
        abstract= True

    name = models.CharField(
        max_length=200,
        verbose_name=_('name')
    )

    slug = models.CharField(
        max_length=200,
        verbose_name=_('slug'),
        unique=True
    )

    TYPE_ENUM = 0
    TYPE_STRING = 1
    TYPE_FLOAT = 2
    TYPE_BOOLEAN = 3
    TYPE_INTEGER = 4
    TYPE_SET = 5

    TYPE_CHOICES = (
            (TYPE_ENUM, _('enum')),
            (TYPE_STRING, _('string')),
            (TYPE_FLOAT, _('float')),
            (TYPE_BOOLEAN, _('boolean')),
            (TYPE_INTEGER, _('integer')),
            (TYPE_SET, _('set')),
        )

    type = models.IntegerField(
        null = False,
        blank = False,
        choices=TYPE_CHOICES,
        verbose_name = _('atttribute type')
    )

    unit = models.ForeignKey(
        MeasureUnit,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name=_('measure unit')
    )

    def __str__(self):
        return self.name

    def format_value(self, value):
        if self.type == Attribute.TYPE_ENUM:
            choice = self.choices.filter(id=value).values('value')
            if len(choice) > 0:
                choice = choice[0]
                choice_value = choice['value']
                return choice_value
            else:
                return mark_safe('<big><strong>O LA LA 2</strong></big>')
        else:
            return value

    def get_slug(self):
        if not self.slug:
            self.slug = slugify(self.name, 'ru')
            self.save()
        return self.slug


class AttributeValue(models.Model):
    """
    base abstract EAV value
    """
    class Meta:
        abstract= True

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    int_value = models.BigIntegerField(
        verbose_name = _('integer value'),
        null=True,
        blank=True,
        db_index=True,
    )

    flt_value = models.FloatField(
        verbose_name=_('float value'),
        null=True,
        blank=True,
        db_index=True,
    )

    str_value = models.CharField(
        verbose_name = _('string value'),
        max_length=250,
        null=True,
        blank=True,
        db_index=True,
    )

    txt_value = models.TextField(
        verbose_name = _('long string value'),
        null=True,
        blank=True,
    )

    @property
    def value(self):
        if self.attribute.type == Attribute.TYPE_ENUM:
            if not self.int_value:
                return mark_safe('<big><strong>O LA LA</strong></big>')
            return self.attribute.format_value(self.int_value)
        if self.attribute.type == Attribute.TYPE_STRING:
            return self.str_value
        if self.attribute.type == Attribute.TYPE_FLOAT:
            return self.flt_value
        if self.attribute.type == Attribute.TYPE_BOOLEAN:
            return self.int_value
        if self.attribute.type == Attribute.TYPE_INTEGER:
            return self.int_value

    def __str__(self):
        return str(self.value)


class AttributeChoice(models.Model):
    class Meta:
        abstract= True

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='choices',
        related_query_name='choice',
    )

    value = models.CharField(
        max_length=200,
        verbose_name=_('value')
    )

    order = models.IntegerField(
        verbose_name=_('sort order'),
        null=False,
        blank=False,
        default=0
    )

    def __str__(self):
        return self.value


