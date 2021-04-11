from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import *
from transliterate import slugify
import csv
from random import randint
import requests
from requests.auth import HTTPBasicAuth
import os
import xmltodict
import pprint
from django.db import connection

from data.icecat_v1.icecat_printstore import ICECAT_PRINTSTORE
from data.icecat_v1.icecat_brands import ICECAT_USED_BRANDS

class Command(BaseCommand):

    help = "Seed parsed Icecat data"

    ICECAT_USED_CATEGORIES = []
    ICECAT_USED_MEASURES = []
    ICECAT_FEATURE_GROUPS_SRC = []
    ICECAT_CAT_FEGR_RELATIONS_SRC = []
    ICECAT_USED_FEATURES = []
    ICECAT_USED_BRANDS = []
    ICECAT_PRINTSTORE = []

    ICECAT_MEASURES = dict()
    ICECAT_CATEGORIES_SRC = dict()
    ICECAT_CATEGORIES = dict()
    ICECAT_FEATURE_GROUPS = dict()
    ICECAT_CAT_FEGR_RELATIONS = dict()
    ICECAT_FEGR_CAT = dict()
    ICECAT_FEATURES = dict()
    CAT_SLUGS = dict()
    ATT_SLUGS = dict()
    ICECAT_BRANDS = dict()

    def load_helpers(self, v):

        path = 'data/icecat_v{}/'.format(v)

        #from data.icecat_v2.cat import ICECAT_USED_CATEGORIES
        with open(path+'result-categories.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for r in reader:
                self.ICECAT_USED_CATEGORIES.append((int(r[0]), r[1]))

        #from data.icecat_v2.measures import ICECAT_USED_MEASURES
        with open(path+'result-measures.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|', quoting=csv.QUOTE_NONE)
            for r in reader:
                self.ICECAT_USED_MEASURES.append((int(r[0]), r[1]))

        #from data.icecat_v2.featue_groups import ICECAT_FEATURE_GROUPS as ICECAT_FEATURE_GROUPS_SRC
        with open(path+'result-feature_groups.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for r in reader:
                self.ICECAT_FEATURE_GROUPS_SRC.append((int(r[0]), r[1]))

        # from data.icecat_v2.category_feature_group_relation import ICECAT_CAT_FEGR_RELATIONS as ICECAT_CAT_FEGR_RELATIONS_SRC
        with open(path+'result-category_feature_groups__by_id.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for r in reader:
                self.ICECAT_CAT_FEGR_RELATIONS_SRC.append((int(r[0]), int(r[1]), int(r[2])))

        #from data.icecat_v2.features import ICECAT_USED_FEATURES
        with open(path+'result-features.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for r in reader:
                self.ICECAT_USED_FEATURES.append((int(r[0]), r[1], int(r[2]), int(r[3])))


        #from data.icecat_v2.brands import ICECAT_USED_BRANDS
        # with open(path+'result-features.csv', 'r', encoding='utf-8') as file:
        #     reader = csv.reader(file, delimiter='|')
        #     for r in reader:
        #         self.ICECAT_USED_FEATURES.append((r[0], r[1], r[2], r[2]))


    def create_cat(self, r):

        for attr in ProductAttribute.objects.all():
            self.ATT_SLUGS[attr.slug] = attr

        print('create_cat', r)
        # id, image, parent_id, name_en, name_ru, descr_en, descr_ru

        if r[2] != r[0]:
            if int(r[2]) not in self.ICECAT_CATEGORIES:
                self.create_cat(self.ICECAT_CATEGORIES_SRC[int(r[2])])
            parent = self.ICECAT_CATEGORIES[int(r[2])]
        else:
            parent = None

        slug = slug_base = slugify(r[3] or r[4], language_code='ru')

        counter = 1
        while slug in self.CAT_SLUGS:
            slug = '{}-{}'.format(slug_base, counter)
            counter += 1

        self.CAT_SLUGS[slug] = self.ICECAT_CATEGORIES[int(r[0])] = Category.objects.create(
            icecat_id=r[0],
            slug=slug,
            image_url=r[1],
            name_en=r[3],
            name=r[4] or r[3],
            descr_en=r[5],
            descr=r[6] or r[5],
            parent=parent
        )
        print('>', self.ICECAT_CATEGORIES[int(r[0])])

    def create_attribute_group(self, r):
        print('create_attribute_group', r)
        self.ICECAT_FEATURE_GROUPS[r[0]] = AttributeGroup.objects.create(
            icecat_id=r[0],
            name=r[1],
        )
        print('>', self.ICECAT_FEATURE_GROUPS[r[0]])

    def create_category_attribute_group_relation(self, r):
        assert r[1] in self.ICECAT_CATEGORIES
        assert r[2] in self.ICECAT_FEATURE_GROUPS
        self.ICECAT_CAT_FEGR_RELATIONS[r[0]] = r
        if r[2] not in self.ICECAT_FEGR_CAT:
            self.ICECAT_FEGR_CAT[r[2]] = set()
        self.ICECAT_FEGR_CAT[r[2]].add(r)
        print('>', r)

    def create_measure_unit(self, r):
        self.ICECAT_MEASURES[r[0]] = MeasureUnit.objects.create(
            icecat_id=r[0],
            name=r[1],
        )
        print('>', r)

    def create_attrubute(self, r):
        assert r[2] in self.ICECAT_MEASURES
        assert r[3] in self.ICECAT_CAT_FEGR_RELATIONS

        slug = slug_base = slugify(r[1], language_code='ru')
        counter = 1
        while slug in self.ATT_SLUGS:
            slug = '{}-{}'.format(slug_base, counter)
            counter += 1

        print('create_attrubute: ', slug)

        self.ATT_SLUGS[slug] = self.ICECAT_FEATURES[r[0]] = ProductAttribute.objects.create(
            name=r[1],
            icecat_id=r[0],
            unit=self.ICECAT_MEASURES[r[2]],
            type=Attribute.TYPE_STRING,
            slug=slug
        )
        self.ICECAT_FEATURES[r[0]]._relation = r[2]

        icecat_rel = self.ICECAT_CAT_FEGR_RELATIONS[r[3]]
        icecat_fegrid = icecat_rel[2]
        #print(self.ICECAT_FEGR_CAT[icecat_fegrid])
        relations = []
        for icecat_rel in self.ICECAT_FEGR_CAT[icecat_fegrid]:
            relation = CategoryToProductAttributeRelation(
                category=self.ICECAT_CATEGORIES[icecat_rel[1]],
                attribute=self.ICECAT_FEATURES[r[0]],
                group=self.ICECAT_FEATURE_GROUPS[icecat_rel[2]],
                use_in_filters=False,
                include_in_full_text_index=True,
                show_at_product_page=True,
                main_attribute=False,
                main_relation_attribute=False,
            )
            relations.append(relation)
            #print('>', relation)
        CategoryToProductAttributeRelation.objects.bulk_create(relations)
        print('>', self.ICECAT_FEATURES[r[0]])

    def create_brand(self, r):
        if r[2]:
            self.ICECAT_BRANDS[r[0]] = Brand.objects.filter(name=r[2]).first()
            assert self.ICECAT_BRANDS[r[0]]
            self.ICECAT_BRANDS[r[0]].icecat_id = r[0]
            self.ICECAT_BRANDS[r[0]].save()
        else:
            self.ICECAT_BRANDS[r[0]] = Brand.objects.create(
                name = r[1],
                icecat_id = r[0],
                slug = slugify(r[1], language_code='ru')
            )

    def handle(self, *args, **options):

        self.load_helpers(2)
        path = 'data/icecat_v{}/'.format(2)

        with open('data/icecat_v1/icecat_categories.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for r in reader:
                self.ICECAT_CATEGORIES_SRC[int(r[0])] = r

        for r in self.ICECAT_USED_CATEGORIES:
            if r[0] not in self.ICECAT_CATEGORIES:
                self.create_cat(self.ICECAT_CATEGORIES_SRC[r[0]])

        for r in self.ICECAT_FEATURE_GROUPS_SRC:
            if r[0] not in self.ICECAT_FEATURE_GROUPS:
                self.create_attribute_group(r)

        for r in self.ICECAT_CAT_FEGR_RELATIONS_SRC:
            if r[0] not in self.ICECAT_CAT_FEGR_RELATIONS:
                self.create_category_attribute_group_relation(r)

        for r in self.ICECAT_USED_MEASURES:
            if r[0] not in self.ICECAT_MEASURES:
                self.create_measure_unit(r)

        for r in self.ICECAT_USED_FEATURES:
            if r[0] not in self.ICECAT_FEATURES:
                self.create_attrubute(r)

        for r in ICECAT_USED_BRANDS:
            if r[0] not in self.ICECAT_BRANDS:
                self.create_brand(r)

        for r in ICECAT_PRINTSTORE:
            print(r)
            Product.objects.filter(id=r[0]).update(icecat_id=r[2], icecat_category_id=r[1])

        BRANDS = dict()
        for brand in Brand.objects.exclude(icecat_id=None).all():
            BRANDS[brand.icecat_id] = brand.id

        CATEGORIES = dict()
        for category in Category.objects.exclude(icecat_id=None).all():
            CATEGORIES[category.icecat_id] = category.id

        PRODUCTS = dict()
        for r in ICECAT_PRINTSTORE:
            PRODUCTS[r[2]] = r[0]

        print('len(PRODUCTS)=', len(PRODUCTS))

        SLUGS = dict()
        PARTS = dict()
        for product in Product.objects.exclude(slug=None).all():
            SLUGS[product.slug] = product.id
            PARTS[(product.brand_id, product.part_num)] = product.id
            PRODUCTS[product.icecat_id] = product.id

        print('len(PRODUCTS)=', len(PRODUCTS))

        with open(path+'products.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for i,r in enumerate(reader):
                if not i % 100: print(i)

                try:
                    brand_id = BRANDS[int(r[4])]
                    category_id = CATEGORIES[int(r[5])]
                except Exception as e:
                    print(r)
                    print(e)

                part_num = r[1]
                iceccat_id = int(r[0])

                slug = base_slug = slugify('{}-{}'.format(part_num, r[3]), language_code='ru')
                counter = 1
                while slug in SLUGS:
                    #print('SLUG {} exists'.format(slug, brand_id, part_num))
                    slug = '{}-{}'.format(base_slug, counter)
                    counter += 1

                if iceccat_id in PRODUCTS:
                    Product.objects.filter(id=r[0]).update(
                        _title=r[3] or r[2],
                        description=r[9] or r[8] or r[7] or r[6],
                    )
                elif (brand_id, part_num) in PARTS:
                    Product.objects.filter(part_num=part_num, brand_id=brand_id).update(
                        _title=r[3] or r[2],
                        description=r[9] or r[8] or r[7] or r[6]
                    )
                    print('UPDATE', part_num, brand_id)
                else:
                    try:
                        prod = Product.objects.create(
                            part_num=part_num,
                            name=r[2],
                            _title=r[3] or r[2],
                            description=r[9] or r[8] or r[7] or r[6],
                            icecat_id=iceccat_id,
                            brand_id=brand_id,
                            category_id=category_id,
                            slug=slug
                        )
                        PRODUCTS[iceccat_id] = prod.id
                        SLUGS[slug] = prod.id
                    except Exception as err:
                        print('------------- Error', r[2], int(r[4]), err.__str__())

        ATTRIBUTES = dict()
        for attr in ProductAttribute.objects.all():
            ATTRIBUTES[attr.icecat_id] = attr.id

        product_attributes_values = []

        with open(path+'features_values.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|', quotechar=None)
            for i,r in enumerate(reader):
                if not i % 100: print(i)
                # product_id, feature_id, feature_group_id[1], value, measure_id
                try:
                    product_id = PRODUCTS[int(r[0])]
                except:
                    print('Product [{}] not found feature 3)'.format(r[0]))
                    continue

                try:
                    attr_id = ATTRIBUTES[int(r[1])]
                except:
                    print('Attribute [{}] not found'.format(r[1]))
                    continue

                txt_value = None
                if len(r[3])>1000:
                    print('Value [{}] is too big'.format(r[3]))
                    txt_value = r[3]

                product_attributes_values.append(ProductAttributeValue(
                    product_id=product_id,
                    attribute_id=attr_id,
                    str_value=r[3][:250],
                    txt_value=txt_value
                ))

                if i and not i % 5000:
                    ProductAttributeValue.objects.bulk_create(product_attributes_values)
                    product_attributes_values = []

        ProductAttributeValue.objects.bulk_create(product_attributes_values)

        product_images = []

        with open(path+'images.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for i,r in enumerate(reader):
                if not i % 100: print(i)
                try:
                    product_id = PRODUCTS[int(r[0])]
                except:
                    print('Product [{}] not found (image 4)'.format(r[0]))
                    continue
                product_images.append(ProductImage(
                    product_id=product_id,
                    external=r[1]
                ))

                if i and not i % 5000:
                    ProductImage.objects_all.bulk_create(product_images)
                    product_images = []

        ProductImage.objects_all.bulk_create(product_images)

        product_related = []

        with open(path+'related.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for i,r in enumerate(reader):
                if not i % 100: print(i)
                try:
                    product0_id = PRODUCTS[int(r[0])]
                except:
                    print('Related product [{}] not found (1)'.format(r[0]))
                    continue
                try:
                    product1_id = PRODUCTS[int(r[1])]
                except:
                    print('Related roduct [{}] not found (2)'.format(r[1]))
                    continue
                product_related.append(ProductToProduct(
                    product_base_id=product0_id,
                    product_related_id=product1_id
                ))

                if i and not i % 5000:
                    ProductToProduct.objects.bulk_create(product_related, ignore_conflicts=True)
                    product_related = []

        ProductToProduct.objects.bulk_create(product_related, ignore_conflicts=True)

        query = """
        DELETE
        FROM `catalog_categorytoproductattributerelation` 
        WHERE (attribute_id, category_id) NOT IN (
            SELECT DISTINCT `catalog_productattributevalue`.`attribute_id`, `catalog_product`.`category_id` 
            FROM `catalog_productattributevalue` INNER JOIN `catalog_product` ON (`catalog_productattributevalue`.`product_id` = `catalog_product`.`id`) )
        """

        with connection.cursor() as c:
            c.execute(query)

        self.convert_float('Вес')
        self.convert_float('Высота')
        self.convert_float('Высота упаковки')
        self.convert_float('Ширина упаковки')
        self.convert_float('Глубина упаковки')

        self.convert_int('Общий объем подачи бумаги')
        self.convert_int('Число картриджей для печати')
        self.convert_int('Количество портов Ethernet LAN ( RJ-45)')
        self.convert_int('Максимальная вместимость выходного лотка')
        self.convert_int('Количество портов USB 3.2 Gen 1 (3.1 Gen 1) Type-A')
        self.convert_int('Количество портов USB 2.0')

        self.convert_bool('Совместимость с Mac')
        self.convert_bool('Экономичная печать')

        self.convert_enum('Диагональ экрана')
        self.convert_enum('Разрешение печати')
        self.convert_enum('Левая граница печати (A4)')
        self.convert_enum('Скорость печати (цвет., обычное кач., A3)')

    # from catalog.models import *
    # attr = ProductAttribute.objects.filter(name='Разрешение печати').first()
    # attr._convert_to_enum()
    # attr = ProductAttribute.objects.filter(name='Диагональ экрана').first()
    # attr._convert_to_enum()
    # attr = ProductAttribute.objects.filter(name='Левая граница печати (A4)').first()
    # attr._convert_to_enum()
    # attr = ProductAttribute.objects.filter(name='Скорость печати (цвет., обычное кач., A3)').first()
    # attr._convert_to_enum()

    def convert_int(self, name):
        attr = ProductAttribute.objects.filter(name=name).first()
        attr._convert_to_flt()

    def convert_float(self, name):
        attr = ProductAttribute.objects.filter(name=name).first()
        attr._convert_to_int()

    def convert_bool(self, name):
        attr = ProductAttribute.objects.filter(name=name).first()
        attr._convert_to_boolean()

    def convert_enum(self, name):
        attr = ProductAttribute.objects.filter(name=name).first()
        attr._convert_to_enum()

    def convert_set(self, name):
        attr = ProductAttribute.objects.filter(name=name).first()
        attr._convert_to_set()
