from django.contrib import admin
from django import forms
from catalog.models import *
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseInlineFormSet
from django.urls import NoReverseMatch
from unicat.admin import OptimisedForeignKeyRawIdWidget
from django.urls import include, path, re_path
from django.http import HttpResponseRedirect

class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug':('name',),
    }
#
# class CategoryToProductAttributeRelationInlineForm(forms.Fo):
#   class Meta:
#     model = CategoryToProductAttributeRelation
#     widgets = {
#       'approve_ts': OptimisedForeignKeyRawIdWidget(),
#     }
#     fields = '__all__'
#
# class StopAdmin(admin.ModelAdmin):
#   form = StopAdminForm


from django import forms
from django.contrib import admin

# class CategoryToProductAttributeRelationAdminForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         print("CategoryToProductAttributeRelationAdminForm(forms.ModelForm):")
#         super(CategoryToProductAttributeRelationAdminForm, self).__init__(*args, **kwargs)
#         self.fields['attribute'].widget = OptimisedForeignKeyRawIdWidget(admin_site=admin.site, rel=CategoryToProductAttributeRelationInline)
#         self.fields['group'].widget = OptimisedForeignKeyRawIdWidget(admin_site=admin.site, rel=CategoryToProductAttributeRelationInline)

class CategoryToProductAttributeRelationInline(admin.TabularInline):
#    form = CategoryToProductAttributeRelationAdminForm
    model = CategoryToProductAttributeRelation
    raw_id_fields = ('attribute', 'group')

    def get_field_queryset(self, db, db_field, request):
        qs = super().get_field_queryset(db, db_field, request)
        print('get_field_queryset 1 ')
        if (qs):
            print('get_field_queryset 2', qs.query)
        return qs

    def get_queryset(self, request):
        print('get_queryset 1')
        qs = super().get_queryset(request)
        if (qs):
            print('get_queryset 2', qs.query)
            qs.select_related('attribute')
        return qs

    def get_formset(self, request, obj=None, **kwargs):
        print('get_formset 1')
        fs = super().get_formset(request, obj, **kwargs)
        print('get_formset 2', fs)
        return fs

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        print('formfield_for_dbfield')
        ff = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name=='attribute' or db_field.name=='group':
            print('formfield_for_dbfield 1', ff)
        return ff


class CategoryChildsInline(admin.TabularInline):
    verbose_name = _('Subcategory')
    verbose_name_plural = _('Subcategories')
    model = Category
    fields = ('name', )
    show_change_link = True
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False
    def has_add_permission(self, request, obj=None): return False


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    prepopulated_fields = {
        'slug':('name',),
    }
    inlines = (CategoryToProductAttributeRelationInline, CategoryChildsInline)
    search_fields = ('name', 'id', 'icecat_id')


class AttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    fields = ['attribute', 'int_value', 'str_value', 'flt_value', 'txt_value']
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        print('get_readonly_fields')
        return ['attribute']

    def get_formset(self, request, obj=None, **kwargs):
        print('get_formset')
        return super().get_formset(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        print('get_fieldsets')
        return super().get_fieldsets(request, obj)

    def has_add_permission(self, request, obj):
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        print('formfield_for_dbfield')

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def to_field_allowed(self, request, to_field):
        return super().to_field_allowed(request, to_field)


class AttributeValueInlineAdd(admin.TabularInline):
    model = ProductAttributeValue
    fields = ['attribute', 'int_value', 'str_value', 'flt_value', 'txt_value']
    raw_id_fields = ('attribute',)
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return []


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug':('name',),
    }
    list_display = ('name', 'part_num')
    inlines = (AttributeValueInline, AttributeValueInlineAdd, )
    list_filter = ('category', )
    search_fields = ('part_num', 'name', '_title')


class SlotAttributeChoiceInline(admin.TabularInline):
    model = SlotAttributeChoice


class SlotAttributeAdmin(admin.ModelAdmin):
    _inlines = (SlotAttributeChoiceInline, )
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['type']
        else:
            return []
    def get_inlines(self, request, obj):
        if obj and obj.type == Attribute.TYPE_ENUM:
            return self._inlines
        else:
            return []


class ProductAttributeChoiceInline(admin.TabularInline):
    model = ProductAttributeChoice


class CategoryToProductAttributeRelationInlineRev(admin.TabularInline):
    model = CategoryToProductAttributeRelation
    raw_id_fields = ('category', 'group')


class ProductAttributeAdmin(admin.ModelAdmin):
    model = ProductAttribute
    _inlines_var = (ProductAttributeChoiceInline, )
    _inlines = ( CategoryToProductAttributeRelationInlineRev, )
    fields = ('name', 'type', 'unit', 'icecat_id', 'used_values_count', 'unique_values_count', 'all_values')
    list_display = ('__str__', 'type', 'used_values_count', 'unique_values_count', 'used_values_type')
    search_fields = ('name', 'id', 'icecat_id')
    change_form_template = 'admin/custom/product_attribute_change_form.html'

    def get_urls(self):
        urls = super(ProductAttributeAdmin, self).get_urls()
        custom_urls = [
            path('convert_to_int/<int:pk>/', self.convert_to_int, name='convert_to_int'),
            path('convert_to_flt/<int:pk>/', self.convert_to_flt, name='convert_to_flt'),
            path('convert_to_str/<int:pk>/', self.convert_to_str, name='convert_to_str'),
            path('convert_to_set/<int:pk>/', self.convert_to_set, name='convert_to_set'),
            path('convert_to_enum/<int:pk>/', self.convert_to_enum, name='convert_to_enum'),
        ]
        return custom_urls + urls

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['all_values', 'icecat_id', 'type', 'used_values_count', 'unique_values_count', 'used_values_type']
        else:
            return ['all_values', 'icecat_id', 'used_values_count', 'unique_values_count', 'used_values_type']

    def get_inlines(self, request, obj):
        if obj and obj.type == Attribute.TYPE_ENUM:
            return self._inlines + self._inlines_var
        else:
            return self._inlines

    def all_values(self, obj: ProductAttribute) -> str:
        return mark_safe('<span style="border:solid 1px #cccccc; margin:2px; padding:2px; display:inline-block; background-color:#eeeeee">{}</span>'.format('</span> <span style="border:solid 1px #cccccc; margin:2px; padding:2px; display:inline-block; background-color:#eeeeee"> '.join([str(x) for x in obj.values_as_set()])))
    all_values.short_description = _('All values')
    all_values.allow_tags = True

    def convert_to_int(self, request, pk):
        attr = ProductAttribute.objects.get(pk=pk)
        attr.convert_to_int()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def convert_to_flt(self, request, pk):
        attr = ProductAttribute.objects.get(pk=pk)
        attr.convert_to_flt()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def convert_to_str(self, request, pk):
        attr = ProductAttribute.objects.get(pk=pk)
        attr.convert_to_str()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def convert_to_set(self, request, pk):
        attr = ProductAttribute.objects.get(pk=pk)
        attr.convert_to_set()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def convert_to_enum(self, request, pk):
        attr = ProductAttribute.objects.get(pk=pk)
        attr.convert_to_enum()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ProductAttributeValueAdmin(admin.ModelAdmin):
    model = ProductAttributeValue
    list_display = ('str_value', 'int_value', 'flt_value')
    list_filter = ('attribute',)


class ProductImageAdmin(admin.ModelAdmin):
    model = ProductImage
    raw_id_fields = ('product', )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(AttributeGroup)
admin.site.register(SlotAttribute, SlotAttributeAdmin)
admin.site.register(Slot)
admin.site.register(MeasureUnit)
admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(CategoryToProductAttributeRelation)
admin.site.register(ProductImage, ProductImageAdmin)