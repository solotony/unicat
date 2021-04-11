from django.db import models
from mptt.models import MPTTModel
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse
import logging
from transliterate import slugify

class MeasureUnit(models.Model):
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
        return self.name

class BreadcrumbedObject():

    def get_parent_breadcrumbs(self):
        x= self.get_root_breadcrumbs()
        return x

    def get_breadcrumbs(self):
        breadcrumbs = self.get_parent_breadcrumbs()
        breadcrumbs.append((self.get_absolute_url(), self.__str__()))
        return breadcrumbs

    @staticmethod
    def get_root_breadcrumbs():
        return [(reverse('website:front'), _('Home page')),]


class Attribute(models.Model):
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

    type = models.IntegerField(
        null = False,
        blank = False,
        choices=(
            (TYPE_ENUM, _('enum')),
            (TYPE_STRING, _('string')),
            (TYPE_FLOAT, _('float')),
            (TYPE_BOOLEAN, _('boolean')),
            (TYPE_INTEGER, _('integer')),
        )
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
            return self.choices.filter(id=value).values('value')[0]['value']
        else:
            return value

    def get_slug(self):
        if not self.slug:
            self.slug = slugify(self.name, 'ru')
            self.save()
        return self.slug


class AttributeValue(models.Model):
    class Meta:
        abstract= True

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    int_value = models.BigIntegerField(
        verbose_name = _('integer value'),
        null=True,
        blank=True
    )

    str_value = models.CharField(
        verbose_name = _('string value'),
        max_length=1000,
        null=True,
        blank=True
    )

    flt_value = models.FloatField(
        verbose_name=_('float value'),
        null=True,
        blank=True
    )

    @property
    def value(self):
        if self.attribute.type == Attribute.TYPE_ENUM:
            return self.attribute.format_value(self.int_value)
        if self.attribute.type == Attribute.TYPE_STRING:
            return self.str_value
        if self.attribute.type == Attribute.TYPE_FLOAT:
            return self.flt_value
        if self.attribute.type == Attribute.TYPE_BOOLEAN:
            return self.int_value
        if self.attribute.type == Attribute.TYPE_INTEGER:
            return self.int_value


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


class AttributeGroup(models.Model):

    class Meta:
        verbose_name = _('Attributes group')
        verbose_name_plural = _('Attributes groups')

    name = models.CharField(
        max_length=200,
        verbose_name=_('name')
    )

    def __str__(self):
        return self.name

    icecat_id = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('icecat id'),
    )


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


class Brand(models.Model, BreadcrumbedObject):

    class Meta:
        verbose_name=_('Brand')
        verbose_name_plural=_('Brands')

    name = models.CharField(
        max_length=200,
        verbose_name=_('name'),
        unique=True
    )

    slug = models.SlugField(
        max_length=200,
        verbose_name=_('slug'),
        unique=True
    )

    icecat_id = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index = True,
        verbose_name=_('icecat id'),
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        #return reverse('catalog:brand', args=[self.id])
        return '/{}/'.format(self.slug)

    def get_breadcrumbs(self):
        return super(Brand, self).get_breadcrumbs()


class Category(MPTTModel, BreadcrumbedObject):

    parent = models.ForeignKey(
        'Category',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='childs',
        related_query_name='child',
        verbose_name=_('parent category')
    )

    class Meta:
        verbose_name=_('Category')
        verbose_name_plural=_('Categories')

    name = models.CharField(
        max_length=200,
        verbose_name=_('name')
    )

    name_en = models.CharField(
        max_length=200,
        verbose_name=_('name at english')
    )

    descr = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description')
    )

    descr_en = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description at english')
    )

    # поле будет удалено в будущем
    image_url = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_('image url')
    )

    slug = models.SlugField(
        max_length=200,
        verbose_name=_('slug'),
        unique=True
    )

    attributes = models.ManyToManyField(
        ProductAttribute,
        blank=True,
        verbose_name=_('attributes'),
        through='CategoryToProductAttributeRelation'
    )

    icecat_id = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('icecat id'),
    )

    def __str__(self):
        return self.name

    def get_parent_breadcrumbs(self):
        logging.debug('Category.get_parent_breadcrumbs')
        if self.parent:
            return self.parent.get_breadcrumbs()
        else:
            return self.get_root_breadcrumbs()

    def full_slug(self):
        if self.parent:
            slugs = self.parent.full_slug()
        else:
            slugs = []
        slugs.append(self.slug)
        return slugs

    def get_absolute_url(self):
        #return reverse('catalog:category', args=[self.id])
        return '/{}/'.format('/'.join(self.full_slug()))


class CategoryToProductAttributeRelation(models.Model):

    class Meta:
        unique_together=('category', 'attribute')

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    group = models.ForeignKey(
        AttributeGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    use_in_filters = models.BooleanField(
        default=True,
        verbose_name=_('use in filters')
    )

    show_at_product_page = models.BooleanField(
        default=True,
        verbose_name=_('show at product page')
    )

    include_in_full_text_index = models.BooleanField(
        default=True,
        verbose_name=_("full text"),
        help_text=_("include in full text index")
    )

    order = models.IntegerField(
        verbose_name=_('sort order'),
        null=False,
        blank=False,
        default=0
    )

    main_attribute = models.BooleanField(
        default=False,
        verbose_name=_('main attribute')
    )

    main_relation_attribute = models.BooleanField(
        default=False,
        verbose_name=_('main relation attribute')
    )


class Product(models.Model, BreadcrumbedObject):

    class Meta:
        unique_together=(
            ('part_num', 'brand'),
        )
        verbose_name=_('Product')
        verbose_name_plural=_('Product')

    part_num = models.CharField(
        max_length=100,
        verbose_name=_('part numer'),
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_('name')
    )

    _title = models.CharField(
        max_length=200,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('title')
    )

    printstore_id = models.BigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('PrintStore id'),
    )

    profile_id = models.BigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('PrintStore profile id'),
    )

    icecat_id = models.BigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('icecat id'),
    )

    icecat_category_id = models.BigIntegerField(
        default=None,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('icecat category id'),
    )

    slug = models.SlugField(
        max_length=200,
        verbose_name=_('slug'),
        unique=True
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.DO_NOTHING,
        blank=False,
        null=False,
        related_query_name='product',
        related_name='products',
        verbose_name=_('brand')
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        blank=False,
        null=False,
        related_query_name='product',
        related_name='products',
        verbose_name=_('category')
    )

    related_products = models.ManyToManyField(
        to='Product',
        #symmetrical=True,
        blank=True,
        through='ProductToProduct',
        through_fields=('product_base', 'product_related'),
        verbose_name=_('related products'),
        related_name='related_products_reverse',
        related_query_name = 'related_product_reverse'
    )

    description = models.TextField(
        verbose_name=_('description'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_parent_breadcrumbs(self):
        if self.category:
            return self.category.get_breadcrumbs()
        else:
            return self.get_root_breadcrumbs()

    def full_slug(self):
        slugs = self.category.full_slug()
        slugs.append(self.brand.slug)
        slugs.append(self.slug)
        return slugs

    def get_absolute_url(self):
        #return reverse('catalog:product', args=[self.id])
        return '/{}/'.format('/'.join(self.full_slug()))

    def attribute_value(self, attribute):
        av = self.values.filter(attribute=attribute).first()
        if not av:
            return None
        return av.value

    def icecat_url(self):
        if not self.icecat_id:
            return None
        return 'https://data.icecat.biz/xml_s3/xml_server3.cgi?product_id={};lang=ru;output=productxml'.format(self.icecat_id)

    def title(self):
        if self._title:
            return self._title
        return self.name


class ProductAttributeValue(AttributeValue):

    class Meta:
        unique_together = (
            ('product', 'attribute')
        )

    product = models.ForeignKey(
        Product,
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
        blank=False
    )


class SlotAttribute(Attribute):

    class Meta:
        verbose_name = _('Slot attribute')
        verbose_name_plural = _('Slot attributes')


class SlotAttributeChoice(AttributeChoice):

    class Meta:
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


class ProductToProduct(models.Model):

    class Meta:
        unique_together = ('product_base', 'product_related')

    product_base = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_index=True,
        related_name='relations_a',
        related_query_name = 'relation_a'
    )

    product_related = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_index=True,
        related_name='relations_b',
        related_query_name='relation_b'
    )

    slot = models.ForeignKey(
        Slot,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True
    )

    number_base = models.IntegerField(
        default=1
    )

    number_related = models.IntegerField(
        default=1
    )


class ProductImage(models.Model):

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='images',
        related_query_name='image'
    )

    external = models.URLField(
        verbose_name=_('external image url')
    )

    def get_image_url(self):
        return self.external
