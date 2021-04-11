from django.db import models
from django.utils.translation import ugettext_lazy as _
from catalog.models.breadcrumbed import BreadcrumbedObject

class Brand(models.Model, BreadcrumbedObject):

    class Meta:
        app_label='catalog'
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
