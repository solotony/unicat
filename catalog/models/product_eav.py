from django.db import models
from django.utils.translation import ugettext_lazy as _
from catalog.models.eav import Attribute, AttributeChoice, AttributeValue
from catalog.models.helpers import str_to_float, str_to_int, str_to_ibool

class ProductAttribute(Attribute):

    class Meta:
        verbose_name = _('Product attribute')
        verbose_name_plural = _('Product attributes')

    icecat_id = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('icecat id'),
    )

    unique_values_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('unique values count'),
        help_text=_('calculatable statistics field')
    )

    used_values_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('total values count'),
        help_text=_('calculatable statistics field')
    )

    used_values_type = models.PositiveIntegerField(
        default=None,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('used values type'),
        help_text=_('calculatable statistics field'),
        choices=Attribute.TYPE_CHOICES,
    )

    def values_as_set(self):
        if self.type == Attribute.TYPE_STRING:
            return set(self.values.values_list('str_value', flat=True).distinct())
        elif self.type == Attribute.TYPE_FLOAT:
            return set(self.values.values_list('flt_value', flat=True).distinct())
        else:
            return set(self.values.values_list('int_value', flat=True).distinct())

    def can_convert_type(self):
        return self.type == Attribute.TYPE_STRING

    def convert_to_flt(self):
        self._convert_to_flt()

    def convert_to_int(self):
        self._convert_to_int()

    def convert_to_enum(self):
        self._convert_to_enum()

    def convert_to_boolean(self):
        self._convert_to_boolean()

    def convert_type(self):
        if not self.can_convert_type():
            return False
        if self.used_values_type ==  Attribute.TYPE_FLOAT:
            self._convert_to_flt()
        elif self.used_values_type ==  Attribute.TYPE_INTEGER:
            self._convert_to_int()
        elif self.used_values_type ==  Attribute.TYPE_ENUM:
            self._convert_to_enum()
        elif self.used_values_type ==  Attribute.TYPE_BOOLEAN:
            self._convert_to_boolean()

    def _convert_to_flt(self):
        values = []
        for value in self.values.all():
            value.flt_value = str_to_float(value.str_value, 0.0)
            values.append(value)
        ProductAttributeValue.objects.bulk_update(values, ['flt_value'])
        self.type = Attribute.TYPE_FLOAT
        self.save()

    def _convert_to_int(self):
        values = []
        for value in self.values.all():
            value.int_value = str_to_int(value.str_value, 0)
            values.append(value)
        ProductAttributeValue.objects.bulk_update(values, ['int_value'])
        self.type = Attribute.TYPE_INTEGER
        self.save()

    def _convert_to_boolean(self):
        values = []
        for value in self.values.all():
            value.int_value = str_to_ibool(value.str_value, False)
            values.append(value)
        ProductAttributeValue.objects.bulk_update(values, ['int_value'])
        self.type = Attribute.TYPE_BOOLEAN
        self.save()

    def _convert_to_enum(self):
        values = []
        values_dict = {v:None for v in self.values_as_set()}
        #print(values_dict)
        self.choices.all().delete()
        #choices_list = []
        for value in values_dict:
            choice = ProductAttributeChoice.objects.create(attribute=self, value=value)
            #choices_list.append(choice)
            values_dict[value] = choice
        #ProductAttributeChoice.objects.bulk_create(choices_list)
        for value in self.values.all():
            value.int_value = values_dict[value.str_value].id
            values.append(value)
        ProductAttributeValue.objects.bulk_update(values, ['int_value'])
        self.type = Attribute.TYPE_ENUM
        self.save()

    def _convert_to_set(self):
        # TODO - надо сделать
        assert False

    _by_slug = {}
    @classmethod
    def by_slug(cls, slug:str)->[None, 'ProductAttribute']:
        if slug not in cls._by_slug:
            cls._by_slug[slug] = cls.objects.filter(slug=slug).first()
        return cls._by_slug[slug]

    def can_convert_to_int(self):
        return self.type == Attribute.TYPE_STRING

    def can_convert_to_flt(self):
        return self.type == Attribute.TYPE_STRING

    def can_convert_to_enum(self):
        return self.type == Attribute.TYPE_STRING

    def can_convert_to_set(self):
        return False # TODO self.type == Attribute.TYPE_STRING

    def can_convert_to_str(self):
        return self.type in [Attribute.TYPE_ENUM, Attribute.TYPE_FLOAT, Attribute.TYPE_BOOLEAN,  Attribute.TYPE_INTEGER, Attribute.TYPE_SET]


class ProductAttributeChoice(AttributeChoice):

    class Meta:
        verbose_name = _('Product attribute choice')
        verbose_name_plural = _('Product attribute choices')

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name=_('attribute'),
        related_name='choices',
        related_query_name='choice',
    )


class ProductAttributeValue(AttributeValue):

    class Meta:
        unique_together = (
            ('product', 'attribute')
        )

    product = models.ForeignKey(
        to='Product',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='values',
        related_query_name='value'
    )

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='values',
        related_query_name='value'
    )
