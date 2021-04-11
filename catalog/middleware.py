import logging
from .models import *

class UrlMapperMiddleware:
    '''
    Эта миддлварь мапит хитрые URLы в простые,которые можно уже разбирать регекспом
    а оригинальный URL полюбому запоминается в request.orig_path_info
    '''

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def substitute_path(self, request):
        request.orig_path_info = request.path_info
        slugs = list(filter(None, request.path_info.split('/')))
        if not len(slugs):
            return
        if len(slugs) == 1:
            brand = Brand.objects.filter(slug=slugs[0]).first()
            if brand:
                request.path_info = '/brand/{}/'.format(brand.id)
                return
            category = Category.objects.filter(slug=slugs[0]).first()
            if category:
                request.path_info = '/category/{}/'.format(category.id)
                return
            return
        if len(slugs) > 2:
            product = Product.objects.filter(slug=slugs[-1]).first()
            if product:
                request.path_info = '/product/{}/'.format(product.id)
                return
        category = Category.objects.filter(slug=slugs[-1]).first()
        if category:
            request.path_info = '/category/{}/'.format(category.id)

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        self.substitute_path(request)
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response
