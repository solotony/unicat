from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import *
from transliterate import slugify
import csv
from random import randint
from django.db import connection
from django.db.models import *
from django.db.models.functions import Coalesce
import re

re_boolean = re.compile('^[YN]$')
re_integer = re.compile('^[0-9]+$')
re_float = re.compile('^[0-9.,]+$')

class Command(BaseCommand):
    help = "Calculate atribute statistics"

    def handle(self, *args, **options):

        # print(ProductAttributeValue.objects.filter(attribute_id=234).
        #       values('str_value').
        #       count())
        #
        # print(ProductAttributeValue.objects.filter(attribute_id=234).
        #     values('str_value').
        #     distinct().
        #     count())

        print('0' * 50)

        ProductAttribute.objects.update(
            unique_values_count=Subquery(
                ProductAttributeValue.objects.filter(attribute_id=OuterRef('id')).
                    values('attribute_id').
                    annotate(cnt=Count('str_value', distinct=True)).
                    values('cnt')
            ),
            used_values_count=Subquery(
                ProductAttributeValue.objects.filter(attribute_id=OuterRef('id')).
                    values('attribute_id').
                    annotate(cnt=Count('attribute_id')).
                    values('cnt')
            )
        )

        print('1'*50)

        VALUES_TYPES = dict()

        for i, value in enumerate(ProductAttributeValue.objects.filter(attribute__type=Attribute.TYPE_STRING)):
            if not value.attribute_id in VALUES_TYPES:
                VALUES_TYPES[value.attribute_id] = 0b11111
            if re_boolean.match(value.str_value):
                VALUES_TYPES[value.attribute_id] &= 0b10001
            elif re_integer.match(value.str_value):
                VALUES_TYPES[value.attribute_id] &= 0b01101
            elif re_float.match(value.str_value):
                VALUES_TYPES[value.attribute_id] &= 0b00101
            else:
                VALUES_TYPES[value.attribute_id] &= 0b00001
            if not i%10000:
                print(i)

        print('2' * 50)

        for v in VALUES_TYPES:
            print(v, VALUES_TYPES[v])

        print('3' * 50)

        ATTR_TO_UPDATE = list()

        for attribute in ProductAttribute.objects.all():
            if attribute.id not in VALUES_TYPES:
                continue

            if VALUES_TYPES[attribute.id] == 17:
                attribute.used_values_type = Attribute.TYPE_BOOLEAN
            elif VALUES_TYPES[attribute.id] == 13:
                attribute.used_values_type = Attribute.TYPE_INTEGER
            elif VALUES_TYPES[attribute.id] == 5:
                attribute.used_values_type = Attribute.TYPE_FLOAT
            else:
                attribute.used_values_type = Attribute.TYPE_STRING

            ATTR_TO_UPDATE.append(attribute)

        print('4' * 50)

        ProductAttribute.objects.bulk_update(ATTR_TO_UPDATE, ['used_values_type'])

        print('5' * 50)

