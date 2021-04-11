from django.shortcuts import render, redirect
from django.forms import Form, MultipleChoiceField, CharField, IntegerField, FloatField, NullBooleanField, DecimalField
from django.views.generic import TemplateView, View, ListView, DetailView
from catalog.models import *
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpRequest
from django.db.models import Max, Min
from django.db.models import OuterRef, Subquery, Prefetch
import logging

from common.development import monitor_results

FILTER_BRAND_SLUG = 'filter_brand'
FILTER_TEXT_SLUG = 'filter_text'
FILTER_ATTRUBUTE_PREFIX = 'filter_attribute__'

CATEGORY_PRODUCTS = 20
SUBCATEGORY_PRODUCTS = 5

def number(x, default=0):
    try:
        return int(x)
    except:
        return default


class FrontView(TemplateView):
    template_name = 'website/front.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'title': 'Главная страница',
            'description': 'Описание главной страницы',
            'image': 'https://homepages.cae.wisc.edu/~ece533/images/baboon.png',
            'canonical': '/'
        }
        context['root'] = Category.objects.filter(parent=None)
        return context


class FiltersForm(Form):
    cmd = CharField(required=False)

    def __init__(self, request, filters):
        self.filters = filters  # kwargs.pop('filters', None)
        super().__init__(request.POST)
        for filter in self.filters:
            field_name = filter['slug']
            if filter['type'] == Attribute.TYPE_ENUM:
                self.fields[field_name] = MultipleChoiceField(
                    required=False,
                    choices=filter['choices']
                )
            if filter['type'] == Attribute.TYPE_SET:
                self.fields[field_name] = MultipleChoiceField(
                    required=False,
                    choices=filter['choices']
                )
            elif filter['type'] == Attribute.TYPE_BOOLEAN:
                self.fields[field_name] = NullBooleanField(
                    required=False,
                )
            elif filter['type'] == Attribute.TYPE_INTEGER:
                self.fields[field_name + '--min'] = IntegerField(
                    required=False,
                    min_value=filter['range_min'],
                    max_value=filter['range_max'],
                )
                self.fields[field_name + '--max'] = IntegerField(
                    required=False,
                    min_value=filter['range_min'],
                    max_value=filter['range_max'],
                )
            elif filter['type'] == Attribute.TYPE_FLOAT:
                self.fields[field_name + '--min'] = FloatField(
                    required=False,
                    localize=False,
                    min_value=filter['range_min'],
                    max_value=filter['range_max'],
                )
                self.fields[field_name + '--max'] = FloatField(
                    required=False,
                    localize=False,
                    min_value=filter['range_min'],
                    max_value=filter['range_max'],
                )
            elif filter['type'] == Attribute.TYPE_STRING:
                self.fields[field_name] = CharField(
                    required=False,
                )


class CategoryView(ListView):
    template_name = 'website/category.html'
    paginate_by = CATEGORY_PRODUCTS
    paginate_orphans = 5
    model = Product
    context_object_name = 'products'

    def __init__(self, *args, **kwargs):
        devprt('CategoryView', '__init__')
        super(CategoryView, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        devprt('CategoryView', 'get_context_data')
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['filters'] = self.get_filters()
        context['main_menu_links'] = Category.get_main_menu_links()
        context['is_products'] = True
        context['is_subcategories'] =  self.category.is_childs()
        context['is_filters'] = True
        context['subcategories'] = self.subcategories
        return context

    def dispatch(self, request, *args, **kwargs):
        devprt('CategoryView', 'dispatch')
        self.pk = kwargs.get('pk')
        self._filters = None
        self.category = Category.objects.filter(id=self.pk).prefetch_related('childs').first()
        last_category = request.session.get('last_category', None)
        if last_category != self.pk:
            self.reset_filters(request)
            request.session['last_category'] = self.pk
        # post служать
        if request.method == 'GET':
            devprt('CategoryView', "request.method == 'GET'")
            self.subcategories = []
            for child in self.category.childs.all():
                products = self.get_products_qs(child)[:SUBCATEGORY_PRODUCTS]
                self.subcategories.append({'category':child, 'products':products})
        elif request.method == 'POST':
            devprt('CategoryView', "request.method == 'POST'")
        else:
            devprt('CategoryView', "request.method == {}".format(request.method))


        #subqry = Subquery(Product.objects.filter(category_id=OuterRef('id')).values_list('id', flat=True)[:5])
        #User.objects.prefetch_related(Prefetch('comments', queryset=Comment.objects.filter(id__in=subqry)))
        #self.subcategories = Category.objects.filter(parent_id=self.pk).prefetch_related(Prefetch('products', queryset=Product.objects.filter(id__in=subqry)))
        #print(self.subcategories)

        return super(CategoryView, self).dispatch(request, *args, **kwargs)

    def get_products_qs(self, category):
        devprt('CategoryView', "get_products_qs")
        qs = Product.tree_products_qs(category).\
            select_related('brand', 'category', 'category__parent', 'category__parent__parent',
                           'category__parent__parent__parent', 'category__parent__parent__parent__parent'). \
            prefetch_related('values', 'values__attribute'). \
            prefetch_related('images'). \
            order_by('name')

        for filter in self.get_filters():
            if filter['slug'] == FILTER_BRAND_SLUG and filter['value'] and len(filter['value']):
                qs = qs.filter(brand_id__in=filter['value'])
            if filter['slug'] == FILTER_TEXT_SLUG and filter['value'] and len(filter['value']):
                qs = Product.search(filter['value'], queryset=qs)

            if filter['slug'][:len(FILTER_ATTRUBUTE_PREFIX)] == FILTER_ATTRUBUTE_PREFIX:
                if filter['type'] == Attribute.TYPE_FLOAT:
                    tofilter_max = filter['value_max'] is not None and filter['value_max'] < filter['range_max']
                    tofilter_min = filter['value_min'] is not None and filter['value_min'] > filter['range_min']
                    if  tofilter_max and tofilter_min:
                        qs = qs.filter(value__flt_value__range=(filter['value_min'], filter['value_max']), value__attribute__slug=filter['aslug'])
                    elif tofilter_min:
                        qs = qs.filter(value__flt_value__gte=filter['value_min'], value__attribute__slug=filter['aslug'])
                    elif tofilter_min:
                        qs = qs.filter(value__flt_value__lte=filter['value_max'], value__attribute__slug=filter['aslug'])

                if filter['type'] == Attribute.TYPE_INTEGER:
                    tofilter_max = filter['value_max'] is not None and filter['value_max'] < filter['range_max']
                    tofilter_min = filter['value_min'] is not None and filter['value_min'] > filter['range_min']
                    if  tofilter_max and tofilter_min:
                        qs = qs.filter(value__int_value__range=(filter['value_min'], filter['value_max']), value__attribute__slug=filter['aslug'])
                    elif tofilter_min:
                        qs = qs.filter(value__int_value__gte=filter['value_min'], value__attribute__slug=filter['aslug'])
                    elif tofilter_min:
                        qs = qs.filter(value__int_value__lte=filter['value_max'], value__attribute__slug=filter['aslug'])

                if filter['type'] == Attribute.TYPE_BOOLEAN:
                    if filter['value']==0:
                        qs = qs.filter(value__int_value=0, value__attribute__slug=filter['aslug'])
                    elif filter['value']==1:
                        qs = qs.filter(value__int_value=1, value__attribute__slug=filter['aslug'])

                if filter['type'] == Attribute.TYPE_ENUM:
                    if filter['value'] and len(filter['value']):
                        qs = qs.filter(value__int_value__in=filter['value'], value__attribute__slug=filter['aslug'])
        return qs

    def get_queryset(self):
        devprt('CategoryView', "get_queryset")
        if self.category.is_childs():
            return Product.objects.filter(id=-1).all()
        return self.get_products_qs(self.category)

    @monitor_results
    def get_filters(self):
        devprt('CategoryView', "get_filters")
        if self._filters:
            return self._filters
        self._filters = []

        qs_products = Product.objects.filter(category__in=self.category.get_descendants(include_self=True))

        text_filter = {
            'type': Attribute.TYPE_STRING,
            'slug': FILTER_TEXT_SLUG,
            'aslug': FILTER_TEXT_SLUG,
            'name': _('Any Text'),
            'value': self.request.session.get(FILTER_TEXT_SLUG),
        }
        self._filters.append(text_filter)

        brands_filter = {
            'type': Attribute.TYPE_ENUM,
            'slug': FILTER_BRAND_SLUG,
            'aslug': FILTER_BRAND_SLUG,
            'name': _('Brand'),
            'value': self.request.session.get(FILTER_BRAND_SLUG),
            'choices': [(brand.id, brand.name) for brand in Brand.objects.all()],
            'active_choices': set(qs_products.values_list('brand_id', flat=True).distinct())
        }
        self._filters.append(brands_filter)

        qs = self.category.attributes.filter(ctpa_relation__use_in_filters=True)
        for attribute in qs.all():
            slug = FILTER_ATTRUBUTE_PREFIX + attribute.get_slug()
            existing_attribute_values = ProductAttributeValue.objects. \
                filter(attribute=attribute, product__in=qs_products)
            if attribute.type == Attribute.TYPE_ENUM:
                active_choces = set(existing_attribute_values.values_list('int_value', flat=True).distinct())
                filter = {
                    'type': Attribute.TYPE_ENUM,
                    'slug': slug,
                    'aslug':attribute.slug,
                    'name': attribute.name,
                    'value': self.request.session.get(slug),
                    'choices': [(choice.id, choice.value) for choice in attribute.choices.all()],
                    'active_choices': active_choces
                }
                self._filters.append(filter)
            elif attribute.type == Attribute.TYPE_BOOLEAN:
                active_choces = set(existing_attribute_values.values_list('int_value', flat=True).distinct())
                filter = {
                    'type': Attribute.TYPE_BOOLEAN,
                    'slug': slug,
                    'aslug': attribute.slug,
                    'name': attribute.name,
                    'value': self.request.session.get(slug),
                    'choices': [(choice.id, choice.value) for choice in attribute.choices.all()],
                    'active_choices': active_choces
                }
                self._filters.append(filter)
            elif attribute.type == Attribute.TYPE_INTEGER:
                range = existing_attribute_values.aggregate(Min('int_value'), Max('int_value'))
                filter = {
                    'type': Attribute.TYPE_INTEGER,
                    'slug': slug,
                    'aslug': attribute.slug,
                    'name': attribute.name,
                    'value_min': self.request.session.get(slug + '--min', range.get('int_value__min')),
                    'value_max': self.request.session.get(slug + '--max', range.get('int_value__max')),
                    'range_min': range.get('int_value__min'),
                    'range_max': range.get('int_value__max'),
                }
                self._filters.append(filter)
            elif attribute.type == Attribute.TYPE_FLOAT:
                range = existing_attribute_values.aggregate(Min('flt_value'), Max('flt_value'))
                filter = {
                    'type': Attribute.TYPE_FLOAT,
                    'slug': slug,
                    'aslug': attribute.slug,
                    'name': attribute.name,
                    'value_min': self.request.session.get(slug + '--min', range.get('flt_value__min')),
                    'value_max': self.request.session.get(slug + '--max', range.get('flt_value__max')),
                    'range_min': range.get('flt_value__min'),
                    'range_max': range.get('flt_value__max'),
                }
                self._filters.append(filter)
            elif attribute.type == Attribute.TYPE_STRING:
                pass
                # filter = {
                #     'type': Attribute.TYPE_STRING,
                #     'slug': slug,
                #     'aslug': attribute.slug,
                #     'name': attribute.name,
                #     'value': self.request.session.get(slug),
                # }
                # self._filters.append(filter)
        return self._filters

    def save_filters(self, request: HttpRequest):
        devprt('CategoryView', "save_filters")
        form = FiltersForm(request, self.get_filters())
        if form.is_valid():
            for filter in self.get_filters():
                if filter['type'] == Attribute.TYPE_ENUM or filter['type'] == Attribute.TYPE_SET:
                    request.session[filter['slug']] = [int(x) for x in form.cleaned_data.get(filter['slug'])]
                if filter['type'] == Attribute.TYPE_BOOLEAN:
                    print('TYPE_BOOLEAN', form.cleaned_data.get(filter['slug']))
                    value = form.cleaned_data.get(filter['slug'])
                    if value is not None:
                        request.session[filter['slug']] = 1 if value else 0
                    else:
                        request.session.pop(filter['slug'], None)
                if filter['type'] == Attribute.TYPE_INTEGER or filter['type'] == Attribute.TYPE_FLOAT:
                    value_min = form.cleaned_data.get(filter['slug'] + '--min')
                    value_max = form.cleaned_data.get(filter['slug'] + '--max')
                    if value_min is not None and (filter['range_min'] > value_min or filter['range_max'] < value_min):
                        value_min = None
                    if value_max is not None and (filter['range_min'] > value_max or filter['range_max'] < value_max):
                        value_max = None
                    if value_max is not None and value_min is not None and value_max < value_min:
                        value_max, value_min = value_min, value_max
                    if value_min is not None:
                        request.session[filter['slug'] + '--min'] = value_min
                    else:
                        request.session.pop(filter['slug'] + '--min', None)
                    if value_max is not None:
                        request.session[filter['slug'] + '--max'] = value_max
                    else:
                        request.session.pop(filter['slug'] + '--max', None)
                if filter['type'] == Attribute.TYPE_STRING:
                    value = form.cleaned_data.get(filter['slug'])
                    if value is not None:
                        request.session[filter['slug']] = value
                    else:
                        request.session.pop(filter['slug'], None)
        else:
            logging.error(str(form.errors))

    def reset_filters(self, request: HttpRequest):
        devprt('CategoryView', "reset_filters")
        for filter in self.get_filters():
            if filter['type'] == Attribute.TYPE_INTEGER or filter['type'] == Attribute.TYPE_FLOAT:
                request.session.pop(filter['slug'] + '--min', None)
                request.session.pop(filter['slug'] + '--max', None)
                request.session.modified = True
            else:
                request.session.pop(filter['slug'], None)
        self._filters = None

    def post(self, request, *args, **kwargs):
        devprt('CategoryView', "post")
        if request.POST.get('cmd') == 'setfilter':
            self.save_filters(request)
        if request.POST.get('cmd') == 'resetfilter':
            self.reset_filters(request)
        return redirect(request.orig_path_info)


class BrandsView(ListView):
    template_name = 'website/brands.html'
    model = Brand
    context_object_name = 'brands'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BrandView(DetailView):
    template_name = 'website/brand.html'
    model = Brand
    context_object_name = 'brand'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductView(TemplateView):
    template_name = 'website/product.html'

    def __init__(self, *args, **kwargs):
        super(ProductView, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk')

        # subqry = Subquery(Product.objects.filter(category_id=OuterRef('id')).values_list('id', flat=True)[:5])
        # qs = Subquery(AttributeGroup.objects.filter(category_id=OuterRef('category_id')))
        # #sq = Subquery(AttributeGroup.objects.filter(category_id=OuterRef('category_id')).filter(attribute_id=OuterRef('values__attribute_id')))

        self.product = Product.objects.filter(id=self.pk). \
            prefetch_related('values', 'values__attribute', 'values__attribute__unit', 'images', 'category',
                             'values__attribute__ctpa_relations__group').prefetch_related('images').first()
        return super(ProductView, self).dispatch(request, *args, **kwargs)


class SearchView(ListView):
    template_name = 'website/search.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 20
    paginate_orphans = 5

    def __init__(self, *args, **kwargs):
        super(SearchView, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['search_string'] = self.query
        context['search_mode'] = self.search_mode
        context['breadcrumbs'] = Breadcrumbs(_('Search page'))
        return context

    def dispatch(self, request, *args, **kwargs):
        self.query = request.GET.get('query')
        self.search_mode = number(request.GET.get('search_mode', 0), 0)
        self.catid = request.GET.get('catid')
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = Product.search(self.query, self.catid, queryset=qs, search_mode=self.search_mode)
        qs = Product.select_url_needed_staff(qs).order_by('name').\
            prefetch_related('values').\
            prefetch_related('values__attribute').\
            prefetch_related('images')
        return qs
