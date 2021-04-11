from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel
import logging

from catalog.models.breadcrumbed import BreadcrumbedObject


class AttributeGroup(models.Model):

    class Meta:
        app_label = 'catalog'
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


class Category(MPTTModel, BreadcrumbedObject):


    class Meta:
        app_label='catalog'
        verbose_name=_('Category')
        verbose_name_plural=_('Categories')

    parent = models.ForeignKey(
        'Category',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='childs',
        related_query_name='child',
        verbose_name=_('parent category')
    )

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
        to='ProductAttribute',
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

    #TODO эту функцию надо кешировать конечно же
    @classmethod
    def get_main_menu_links(cls):
        qs = cls.objects.filter(parent_id__in=[1, 2, 34]).select_related('parent')
        menu_links = []
        for category in qs.all():
            menu_links.append((category.parent.name+'> '+category.name, category.get_absolute_url(), None, 'default'))
        return menu_links

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_childs = None

    def is_childs(self):
        #print('self._is_childs', 0, self._is_childs)
        if self._is_childs is None:
            #print('self._is_childs', 1, self._is_childs)
            self._is_childs = self.childs.exists()
        #print('self._is_childs', 2, self._is_childs)
        return self._is_childs


# class CategoryToProductAttributeRelationManager(models.Manager):
#
#     def get_queryset(self):
#         qs = super().get_queryset()
#         qs.select_related('group', 'category', 'attrubute')
#         return qs


class CategoryToProductAttributeRelation(models.Model):

    # objects = CategoryToProductAttributeRelationManager()

    class Meta:
        app_label = 'catalog'
        unique_together=('category', 'attribute')

    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='ctpa_relations',
        related_query_name='ctpa_relation',
    )

    attribute = models.ForeignKey(
        to='ProductAttribute',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='ctpa_relations',
        related_query_name='ctpa_relation',
    )

    group = models.ForeignKey(
        to=AttributeGroup,
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


