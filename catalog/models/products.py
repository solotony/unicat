from django.db import models
from django.utils.translation import ugettext_lazy as _
import re
from django.utils.html import strip_tags
from django.db.models import Q, QuerySet

from common.functions import get_upload_path
from common.development import devprt

from catalog.models.breadcrumbed import BreadcrumbedObject
from catalog.models.brands import Brand
from catalog.models.slots import Slot
from catalog.models.categories import Category
from catalog.models.product_eav import ProductAttribute
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.fields import ThumbnailerImageField
from django.utils.html import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage


MIN_INDEX_WORD_LENGTH = 2

#количество товаров в блоке индексирования
INDEXER_BLOCK_SIZE = 100

class SearchBm(models.Lookup):
   lookup_name = 'searchbm'
   def as_mysql(self, compiler, connection):
       lhs, lhs_params = self.process_lhs(compiler, connection)
       rhs, rhs_params = self.process_rhs(compiler, connection)
       params = lhs_params + rhs_params
       return 'MATCH (%s) AGAINST (%s IN BOOLEAN MODE)' % (lhs, rhs), params

class SearchDm(models.Lookup):
   lookup_name = 'searchdm'
   def as_mysql(self, compiler, connection):
       lhs, lhs_params = self.process_lhs(compiler, connection)
       rhs, rhs_params = self.process_rhs(compiler, connection)
       params = lhs_params + rhs_params
       return 'MATCH (%s) AGAINST (%s)' % (lhs, rhs), params

models.CharField.register_lookup(SearchBm)
models.TextField.register_lookup(SearchBm)
models.CharField.register_lookup(SearchDm)
models.TextField.register_lookup(SearchDm)


class UpperCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.is_uppercase = kwargs.pop('uppercase', False)
        super(UpperCharField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        value = super(UpperCharField, self).get_prep_value(value)
        return value.upper() if self.is_uppercase else value


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
        max_length=500,
        verbose_name=_('name')
    )

    _title = models.CharField(
        max_length=500,
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
        max_length=500,
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
        to='Category',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._values = None
        self._values_by_attr = dict()
        self._attribute_groups = None

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

    def load_attribute_values(self):
        if self._values is None:
            self._values = self.values.all()
            for value in self._values:
                self._values_by_attr[value.attribute_id] = value

    def attribute_value(self, attribute):
        self.load_attribute_values()
        return self._values_by_attr.get(attribute.id, None)

    def icecat_url(self):
        if not self.icecat_id:
            return None
        return 'https://data.icecat.biz/xml_s3/xml_server3.cgi?product_id={};lang=ru;output=productxml'.format(self.icecat_id)

    def title(self):
        if self._title:
            return self._title
        return self.name

    re_non_word_signs = re.compile(r'[^\w/.-]+')
    re_non_word_signs_strict = re.compile(r'[_/.-]+')
    re_predigit_letter = re.compile(r'^[^0-9]+')
    re_non_word_signs_ex = re.compile(r'(?:^[_/.-]+)|(\s?:[_/.-]+)|(?:[_/.-]+\s)|(?:[_/.-]+$)')

    @classmethod
    def clean_phrase(cls, phrase):
        phrase = cls.re_non_word_signs.sub(' ', phrase.upper())
        phrase = cls.re_non_word_signs_ex.sub(' ', phrase.upper())
        return phrase

    def _build_words(self):
        str = ''
        if self.name is not None: str += ' ' + self.name
        if self.part_num is not None: str += ' ' + self.part_num
        if self._title is not None: str += ' ' + self._title
        if self.description is not None: str += ' ' + strip_tags(self.description)

        # TODO attributes & values

        words = set([x for x in self.clean_phrase(str).split() if len(x) > MIN_INDEX_WORD_LENGTH])
        extrawords = set()
        for word in words:
            extrawords.update(self.re_non_word_signs_strict.sub(' ', word).split()[1:])
        words.update(extrawords)
        for word in words:
            new_word = self.re_predigit_letter.sub('', word)
            if new_word and new_word!=word:
                extrawords.add(new_word)
            new_word = self.re_non_word_signs_strict.sub('', word)
            if new_word and new_word!=word:
                extrawords.add(new_word)

        words.update(extrawords)
        return words

    def build_words(self):
        words = []
        for word in StopWord.filter(self._build_words()):
            words.append(ProductWord(product=self, word=word))
        ProductWord.objects.bulk_create(words, ignore_conflicts=True)

    @classmethod
    def buld_multi_words(cls, quiet=True, delete=True):
        if delete:
            ProductWord.objects.all().delete()
        cnt = Product.objects.count()
        if not quiet:
            print("Count of products to be indexed: {}".format(cnt))
        offset = 0
        while offset < cnt:
            words = []
            # TODO prefetch attribute & values
            for product in Product.objects.all()[offset:offset + INDEXER_BLOCK_SIZE]:
                for word in StopWord.filter(product._build_words()):
                    words.append(ProductWord(product=product, word=word))
            ProductWord.objects.bulk_create(words, ignore_conflicts=True)
            if not quiet:
                print("Indexed {} products".format(offset))
            offset += INDEXER_BLOCK_SIZE

    def _get_index_data(self):
        phrases = ' '.join([self.name or '', self.part_num or '', self._title or '',
                               strip_tags(self.description) or ''])
        return phrases

    def build_index(self):
        index_data = self._get_index_data()
        ProductIndex.objects.create(product=self, index_data=index_data)

    @classmethod
    def buld_multi_index(cls, quiet=True):
        ProductIndex.objects.all().delete()
        cnt = Product.objects.count()
        if not quiet:
            print("Count of products to be indexed: {}".format(cnt))
        offset = 0
        while offset < cnt:
            indexes = []
            for product in Product.objects.all()[offset:offset + INDEXER_BLOCK_SIZE]:
                indexes.append(ProductIndex(product=product, index_data=product._get_index_data()))
            ProductIndex.objects.bulk_create(indexes, ignore_conflicts=True)
            if not quiet:
                print("Indexed {} products".format(offset))
            offset += INDEXER_BLOCK_SIZE

    @classmethod
    def search(cls, phrase:str, category_id=None, queryset=None, search_mode=0):
        devprt('Product.search', 'search_mode', search_mode)
        devprt('Product.search', 'phrase', phrase)
        devprt('Product.search', 'category_id', category_id)
        devprt('Product.search', 'queryset.query', queryset.query)
        words = StopWord.filter(words=set([x.upper() for x in cls.clean_phrase(phrase).split() if len(x) > MIN_INDEX_WORD_LENGTH]))
        if len(words)==0:
            return Product.objects.filter(category_id=-1)
        if queryset is None:
            queryset = Product.objects.get_queryset()
        devprt('Product.search', 'queryset.query', queryset.query)
        for word in words:
            queryset = queryset.filter(word__word__istartswith=word)
        # if category_id:
        #     queryset = queryset.filter(category_id=category_id)
        # if search_mode == 9:
        #     queryset = queryset.filter(index__index_data__searchdm=phrase)
        # elif search_mode == 10:
        #     queryset = queryset.filter(index__index_data__searchbm=phrase)
        # else:
        #     for word in words:
        #         if search_mode==0:
        #             queryset = queryset.filter(word__word__startswith=word)
        #         elif search_mode==1:
        #             queryset = queryset.filter(word__word__contains=word)
        #         elif search_mode==2:
        #             queryset = queryset.filter(word__word__endswith=word)
        #         elif search_mode == 3:
        #             queryset = queryset.filter(word__word=word)
        #         elif search_mode == 4:
        #             queryset = queryset.filter(word__word__iexact=word)
        #         elif search_mode == 5:
        #             queryset = queryset.filter(word__word__exact=word)
        #         if search_mode==6:
        #             queryset = queryset.filter(word__word__istartswith=word)
        #         elif search_mode==7:
        #             queryset = queryset.filter(word__word__icontains=word)
        #         elif search_mode==8:
        #             queryset = queryset.filter(word__word__iendswith=word)

        devprt('Product.search', 'queryset.query', queryset.query)
        return queryset

    @classmethod
    def tree_products_qs(cls, root_category: Category) -> QuerySet:
        return cls.objects.filter(category__in=root_category.get_descendants(include_self=True))

    @classmethod
    def select_url_needed_staff(cls, qs: QuerySet) -> QuerySet:
        return qs.select_related('brand', 'category__parent', 'category__parent__parent',
                          'category__parent__parent__parent', 'category__parent__parent__parent__parent')

    @classmethod
    def favorite_products(cls, category: Category):
        qs = cls.select_url_needed_staff(cls.tree_products_qs(category))
        return qs.order_by('name').all()[:10]

    def __getattr__(self, item):
        if item[:4]!='eav_':
            # Raise AttributeError if attribute value not found.
            raise AttributeError(f'{self.__class__.__name__}.{item} is invalid.')
            # Return attribute value.
        attribute = ProductAttribute.by_slug(item[4:])
        assert attribute
        return self.attribute_value(attribute)

    def get_attribute_groups(self):
        if self._attribute_groups is not None:
            return self._attribute_groups
        groups = dict()
        self.load_attribute_values()

        total_values = 0

        for relation in self.category.ctpa_relations.select_related('group').all():
            if relation.group_id not in groups:
                groups[relation.group_id] = {'group':relation.group, 'values':[], 'col':0 }
                total_values += 1
            if relation.attribute_id in self._values_by_attr:
                groups[relation.group_id]['values'].append(self._values_by_attr[relation.attribute_id])
                total_values += 1

        groups = {group:groups[group] for group in groups if len(groups[group]['values']) and group}
        devprt('Product.get_attribute_groups', groups)
        groups = list(filter(None, groups.values()))
        devprt('Product.get_attribute_groups', groups)

        self._attribute_groups = sorted(groups, key=lambda item: item['group'].name)

        column_0 = 3
        column_1 = 0
        for group in self._attribute_groups:
            if column_0 > column_1:
                group['col'] = 1
                column_1 += 1 + len(group['values'])
            else:
                group['col'] = 0
                column_0 += 1 + len(group['values'])

        return self._attribute_groups

    def main_image_url(self):
        _images = self.images.exclude(image__isnull=True).all()[:1]
        if _images and len(_images):
            return _images[0].small_url()
        return staticfiles_storage.url('img/no_photo.png')

    def filtered_description(self):
        return self.description.replace('\\n', '\n')


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
        to=Slot,
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

class ProductImageManager(models.Manager):
    pass


class ProductGoodImageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(image__isnull=True)


class ProductImage(models.Model):

    files_folder = 'images'

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    objects = ProductGoodImageManager()
    objects_all = ProductImageManager()

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='images',
        related_query_name='image'
    )

    external = models.URLField(
        verbose_name=_('external image url'),
        null=True,
        blank=True,
    )

    def _get_images_upload_path(self, filename):
        return get_upload_path(self.files_folder, filename)

    image = ThumbnailerImageField(
        null=True,
        blank=True,
        verbose_name=_('image'),
        help_text='',
        upload_to=_get_images_upload_path,
    )

    def image_tag(self):
        if (self.image):
            thumb_url = get_thumbnailer(self.image.name)['admin'].url
            return mark_safe('<img src="%s" />' % thumb_url)
        return None
    image_tag.short_description = _('Preview')
    image_tag.allow_tags = True

    def image_thumbnail_url(self, thumbnail_name):
        if (self.image):
            return get_thumbnailer(self.image.name)[thumbnail_name].url
        return None

    def big_image_url(self):
        if (self.image):
            return self.image.url
        return None

    def small_url(self):
        return self.image_thumbnail_url('product_small')

    def tiny_url(self):
        return self.image_thumbnail_url('product_tiny')


class ProductWord(models.Model):
    class Meta:
        unique_together = ('product', 'word')

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_index=True,
        related_name='words',
        related_query_name='word'
    )

    word = UpperCharField(
        max_length=30,
        blank=False,
        null=False,
        db_index=True,
    )


class StopWord(models.Model):

    word = UpperCharField(
        max_length=30,
        blank=False,
        null=False,
        unique=True,
    )

    stop_words = None

    @classmethod
    def load_words(cls):
        cls.stop_words = set(cls.objects.values_list('word', flat=True))

    @classmethod
    def filter(cls, words:set):
        if cls.stop_words is None:
            cls.load_words()
        return words.difference(cls.stop_words)


class ProductIndex(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        db_index=True,
        related_name='indexes',
        related_query_name='index'
    )

    index_data = models.TextField(
        max_length=30,
        blank=False,
        null=False,
        db_index=True,
    )


def category_favorite_products(category):
    return Product.favorite_products(category)

Category.favorite_products = category_favorite_products