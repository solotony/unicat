from django.shortcuts import render
from django.views.generic import TemplateView, View
from catalog.models import Category
from django.http import HttpResponse


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


class DesignView(TemplateView):
    template_name = 'website/design.html'
    pass

