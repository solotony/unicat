from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import *
from transliterate import slugify
import csv
from random import randint
from django.db import connection

class Command(BaseCommand):
    help = "Create full text index indexing"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('CREATE FULLTEXT INDEX `catalog_productindex_lala` ON `catalog_productindex` (`index_data`)')
