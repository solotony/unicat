from django.urls import include, path, re_path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'catalog'

urlpatterns = [

    re_path('^category/(?P<pk>\d+)/$', CategoryView.as_view(), name='category'),
    #path('^category/(?P<category_id>\d+)/(?P<brand_id>\d+)/$', CategoriesView.as_view(), name='filtered_category'),
    re_path('^product/(?P<pk>\d+)/$', ProductView.as_view(), name='product'),
    re_path('^brand/(?P<pk>\d+)/$', BrandView.as_view(), name='brand'),
    re_path('^brands/$', BrandsView.as_view(), name='brands'),
    re_path('^search/$', SearchView.as_view(), name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
        re_path('^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
