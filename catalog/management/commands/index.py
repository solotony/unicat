from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import *
from transliterate import slugify
import csv
from random import randint
from django.db import connection

class Command(BaseCommand):
    help = "Database indexing"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE `catalog_productword`')
            cursor.execute('DELETE FROM `catalog_productword` WHERE 1')
        Product.buld_multi_words(quiet=False, delete=False)
        Product.buld_multi_index(False)

        return