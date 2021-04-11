from django.urls import include, path, re_path
from .views import *

app_name = 'website'

urlpatterns = [
    re_path('^$', FrontView.as_view(), name='front'),
    re_path('^design/$', DesignView.as_view(), name='design')
]
