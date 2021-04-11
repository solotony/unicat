from django.core.management.base import BaseCommand
from catalog.models import ProductImage, Product
from django.db.models import Prefetch, F

# from transliterate import slugify
# import csv
# from random import randint
# import requests
# from requests.auth import HTTPBasicAuth
# import os
# import xmltodict
# import pprint
# from django.db import connection

from data.icecat_v1.icecat_printstore import ICECAT_PRINTSTORE
from data.icecat_v1.icecat_brands import ICECAT_USED_BRANDS

class Command(BaseCommand):
    help = "Seed parsed Icecat data"

    def handle(self, *args, **options):
        with open('data/images_dump.csv', 'w', encoding='utf-8') as file:
            for image in ProductImage.objects_all.annotate(icecat_id=F('product__icecat_id')).all():
                print(image.icecat_id, image.id, image.external, image.image, sep='|', file=file)
