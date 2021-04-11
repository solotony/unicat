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
from threading import Thread
import time
from data.icecat.ids import IDS as ICECATIDS
import collections

IGNORED_CATEGORIES = set([
    '714' # бумага
])

login, password = ('solotony', '1qazxcde32ws!')
THREADS = 10

class Command(BaseCommand):
    help = "Load Icecat data"

    barcode_attr = ProductAttribute.objects.filter(slug=slugify('Штрих код', 'ru')).first()

    def load_files(self):
        print('has part_num:{}'.format(Product.objects.exclude(part_num=None).count()))
        print('no part_num:{}'.format(Product.objects.filter(part_num=None).count()))

        session = requests.session()
        device_category = Category.objects.filter(name='Устройства').first()

        for product in Product.objects.exclude(part_num=None).all():
            brand = str(product.brand).upper()
            partno = str(product.part_num).upper()
            filename = slugify(brand + '__' + partno, 'ru') +'.xml'
            url = 'https://data.icecat.biz/xml_s3/xml_server3.cgi?prod_id={};vendor={};lang=ru;output=productxml'.format(partno, brand)
            res = session.get(url, auth=HTTPBasicAuth(login, password))
            if res.status_code == 200:
                with open(os.path.join('icecat_download/', filename), 'w', encoding='utf-8') as file:
                    print(res.text, file=file)
            else:
                print('FAIL cat=[{}] brand=[{}] part_num=[{}]'.format(product.category, product.brand, product.part_num))


        PARTS = set()
        for product in Product.objects.filter(part_num=None).all():
            brand = str(product.brand).upper()

            for name_part in product.name.split():
                partno = name_part.upper()
                if partno in PARTS:
                    continue
                PARTS.add(partno)
                filename = slugify(brand + '__' + partno, 'ru') +'.xml'
                url = 'https://data.icecat.biz/xml_s3/xml_server3.cgi?prod_id={};vendor={};lang=ru;output=productxml'.format(partno, brand)
                res = session.get(url, auth=HTTPBasicAuth(login, password))
                if res.status_code == 200:
                    with open(os.path.join('icecat_download/', filename), 'w', encoding='utf-8') as file:
                        print(res.text, file=file)
                else:
                    print('FAIL cat=[{}] brand=[{}] part_num=[{}]'.format(product.category, product.brand, product.part_num))


        PARTS = set()
        for product in Product.objects.exclude(part_num=None).\
                filter(category__in=device_category.get_descendants(include_self=True)).all():
            brand = str(product.brand).upper()
            partno = str(product.part_num).upper()
            filename = slugify(brand + '__' + partno, 'ru') +'.xml'
            if not os.path.exists(os.path.join('icecat_download/by_partno_no/', filename)):
                continue
            print('cat=[{}] brand=[{}] part_num=[{}] name=[{}]'.format(product.category, product.brand, product.part_num, product.name))
            for name_part in product.name.replace(',',' ').split():
                partno = name_part.upper()
                if partno in PARTS:
                    continue
                PARTS.add(partno)
                filename = slugify(brand + '__' + partno, 'ru') +'.xml'
                url = 'https://data.icecat.biz/xml_s3/xml_server3.cgi?prod_id={};vendor={};lang=ru;output=productxml'.format(partno, brand)
                res = session.get(url, auth=HTTPBasicAuth(login, password))
                if res.status_code == 200:
                    with open(os.path.join('icecat_download/', filename), 'w', encoding='utf-8') as file:
                        print(res.text, file=file)
                else:
                    print('FAIL cat=[{}] brand=[{}] part_num=[{}]'.format(product.category, product.brand, product.part_num))

    def load_url(self, id):
        if id <= 13584166:
            print(id, 'SKIP')
            return
        url = 'https://data.icecat.biz/xml_s3/xml_server3.cgi?product_id={};lang=ru;output=productxml'.format(id)
        res = self.session.get(url, auth=HTTPBasicAuth(login, password))
        if res.status_code != 200:
            print('status-code={} id=[{}]'.format(res.status_code, id))
            return
        filename = '{}.xml'.format(id)
        with open(os.path.join('data/icecat/files/', filename), 'w', encoding='utf-8') as file:
            print(res.text, file=file)
            print(id, 'OK')


    def load_from_ids(self, ids):
        self.session = requests.session()
        it = iter(ids)
        start_at = time.time()
        counter = 0
        finish = False
        while True:
            if finish:
                break
            threads = [None]*THREADS
            for i in range(THREADS):
                try:
                    id = next(it)
                    threads[i] = Thread(target=self.load_url, args=(id,))
                    threads[i].start()
                except StopIteration as e:
                    finish = True
                    pass
            for i in range(THREADS):
                if threads[i] is not None:
                    threads[i].join()
            counter += 10
            t = time.time() - start_at
            e = t / counter * (len(ids)-counter)
            print('-- TIME USED: {}  ESTIMATED: {}'.format(t, e))



    def list_files(self):
        device_category = Category.objects.filter(name='Устройства').first()
        for product in Product.objects.exclude(part_num=None).all():
            brand = str(product.brand).upper()
            partno = str(product.part_num).upper()
            filename = slugify(brand + '__' + partno, 'ru') +'.xml'
            if not os.path.exists(os.path.join('icecat_download/by_partno/', filename)):
                continue
            print(1, product.id, filename, sep=';')


        PARTS = set()
        for product in Product.objects.filter(part_num=None).all():
            brand = str(product.brand).upper()

            for name_part in product.name.split():
                partno = name_part.upper()
                if partno in PARTS:
                    continue
                PARTS.add(partno)
                filename = slugify(brand + '__' + partno, 'ru') +'.xml'
                if not os.path.exists(os.path.join('icecat_download/by_name/', filename)):
                    continue
                print(2, product.id, filename, sep=';')


        PARTS = set()
        for product in Product.objects.exclude(part_num=None).\
                filter(category__in=device_category.get_descendants(include_self=True)).all():
            brand = str(product.brand).upper()
            partno = str(product.part_num).upper()
            filename = slugify(brand + '__' + partno, 'ru') +'.xml'
            for name_part in product.name.replace(',',' ').split():
                partno = name_part.upper()
                if partno in PARTS:
                    continue
                PARTS.add(partno)
                filename = slugify(brand + '__' + partno, 'ru') +'.xml'
                if not os.path.exists(os.path.join('icecat_download/by_name2/', filename)):
                    continue
                print(3, product.id, filename, sep=';')

    def process_files(self, ver):

        srcpath = '../data/icecat-v{}/files'.format(ver)
        respath = '../data/icecat-v{}/procfiles'.format(ver)
        path = 'data/icecat-v{}/'.format(ver)

        with open(path + 'products.csv', 'w', encoding='utf-8') as icecat_products: pass
        with open(path + 'images.csv', 'w', encoding='utf-8') as icecat_images: pass
        with open(path + 'features_values.csv'.format(ver), 'w', encoding='utf-8') as icecat_features: pass
        with open(path + 'related.csv', 'w', encoding='utf-8') as icecat_related: pass

        MEASURES = dict()
        LOCAL_MEASURES = dict()
        FEATURE_GROUPS = dict()
        CATEGORY_FEATURE_GROUPS__BY_CAT = dict()
        CATEGORY_FEATURE_GROUPS__BY_ID = dict()
        CATEGORIES = dict()
        FEATURES = dict()
        PRODUCT_FEATURES = dict()
        PRODUCT_RELATED = dict()
        PRODUCT_IMAGES = dict()
        DETECTED_PRODUCTS = dict()
        SUPPLIERS = dict()
        PRODUCTS = dict()
        COUNTER = {'x':0}

        def process_file(full_filename):
         COUNTER['x'] += 1
         if not os.path.exists(full_filename):
          return
         print(full_filename)
         with open(path + 'products.csv', 'a', encoding='utf-8') as icecat_products:
          with open(path + 'images.csv', 'a', encoding='utf-8') as icecat_images:
           with open(path + 'features_values.csv', 'a', encoding='utf-8') as icecat_features:
            with open(path + 'related.csv', 'a', encoding='utf-8') as icecat_related:
             with open(full_filename, 'r', encoding='utf-8') as file:
                s = file.read()
                d = xmltodict.parse(s)
                dd = d['ICECAT-interface']['Product']
                if 'Category' not in dd:
                    print('skip file')
                    return
                category_id = dd['Category']['@ID']

                product_id = dd['@ID']
                if product_id in PRODUCTS:
                    print("{} {} dublicated".format(COUNTER['x'], product_id))
                    return

                print("{} {} {}".format(COUNTER['x'], product_id, dd['@Title']))
                SUPPLIERS[dd['Supplier']['@ID']] = dd['Supplier']['@Name']

                description = ''
                summary_short_description = ''
                summary_long_description = ''
                descr_short_description = ''
                descr_long_description = ''
                descr_warranty = ''
                if dd.get('SummaryDescription'):
                    if dd['SummaryDescription'].get('ShortSummaryDescription'):
                        summary_short_description = dd['SummaryDescription']['ShortSummaryDescription'].get('#text')
                    if dd['SummaryDescription'].get('LongSummaryDescription'):
                        summary_long_description = dd['SummaryDescription']['LongSummaryDescription'].get('#text')
                if dd.get('ProductDescription'):
                    if dd['ProductDescription'].get('@LongDesc'):
                        descr_long_description = dd['ProductDescription'].get('@LongDesc')
                    if dd['ProductDescription'].get('@ShortDesc'):
                        descr_short_description = dd['ProductDescription'].get('@ShortDesc')
                    if dd['ProductDescription'].get('@WarrantyInfo'):
                        descr_warranty = dd['ProductDescription'].get('@WarrantyInfo')
                product = [
                    product_id,
                    dd['@Prod_id'],
                    dd['@Name'],
                    dd['@Title'].replace('|',';'),
                    dd['Supplier']['@ID'],
                    dd['Category']['@ID'],
                    summary_short_description.replace('|',';'),
                    summary_long_description.replace('|',';'),
                    descr_short_description.replace('|',';'),
                    descr_long_description.replace('|',';'),
                    descr_warranty.replace('|',';'),
                ]
                print('|'.join(product), file=icecat_products)
                PRODUCTS[product_id] = True

                if product_id not in PRODUCT_FEATURES:
                    PRODUCT_FEATURES[product_id] = list()
                    PRODUCT_RELATED[product_id] = set()
                    PRODUCT_IMAGES[product_id] = set()

                if category_id not in CATEGORIES:
                    CATEGORIES[category_id] = dd['Category']['Name']['@Value']
                    CATEGORY_FEATURE_GROUPS__BY_CAT[category_id] = set()

                del dd['Category']

                if dd.get('CategoryFeatureGroup'):
                    for x in dd['CategoryFeatureGroup']:
                        #print('type(x)', type(x))
                        if type(x) != collections.OrderedDict:
                            continue
                        #print("type(x['FeatureGroup'])", type(x['FeatureGroup']))
                        if type(x['FeatureGroup']) in [dict, collections.OrderedDict]:
                            if x['FeatureGroup']['@ID'] not in FEATURE_GROUPS:
                                FEATURE_GROUPS[x['FeatureGroup']['@ID']] = (x['FeatureGroup']['Name']['@Value'])
                        CATEGORY_FEATURE_GROUPS__BY_CAT[category_id].add((x['@ID'], x['FeatureGroup']['@ID']))
                        CATEGORY_FEATURE_GROUPS__BY_ID[x['@ID']] = (category_id, x['FeatureGroup']['@ID'])

                    del dd['CategoryFeatureGroup']

                if dd.get('ProductFeature'):
                    def sub(x):
                        feature_id = x['Feature']['@ID']
                        measure_id = x['Feature']['Measure']['@ID']
                        value = x['@Value']
                        presentation_value = x['@Presentation_Value']
                        local_value = ''
                        local_measure_id = ''

                        if measure_id not in MEASURES:
                            MEASURES[measure_id] = \
                                x['Feature']['Measure']['Signs']['Sign']['#text'] \
                                    if x['Feature']['Measure']['Signs'] else None

                        if feature_id not in FEATURES:
                            FEATURES[feature_id] = (x['Feature']['Name']['@Value'], measure_id, x.get('@CategoryFeatureGroup_ID'))

                        if x['LocalValue']['@Value']:
                            local_value = x['LocalValue']['@Value']
                            local_measure_id = x['LocalValue']['Measure']['@ID']
                            if 'Signs' in x['LocalValue']['Measure']:
                                if type(x['LocalValue']['Measure']['Signs']) in[list,collections.OrderedDict]:
                                    if 'Sign' in x['LocalValue']['Measure']['Signs']:
                                        if local_measure_id not in LOCAL_MEASURES:
                                            LOCAL_MEASURES[local_measure_id] = \
                                                x['LocalValue']['Measure']['Signs']['Sign']['#text'] \
                                                    if x['LocalValue']['Measure']['Signs']['Sign']['#text'] else None
                        else:
                            value = x['@Value']

                        feature_group_id = CATEGORY_FEATURE_GROUPS__BY_ID.get(x.get('@CategoryFeatureGroup_ID'))
                        #PRODUCT_FEATURES[product_id].append((feature_id, feature_group_id[1], value, measure_id))
                        print('|'.join([product_id, feature_id, feature_group_id[1], value, measure_id, local_value, local_measure_id]), file=icecat_features)

                    if type(dd['ProductFeature']) == list:
                        for x in dd['ProductFeature']:
                            sub(x)
                    else:
                        sub(dd['ProductFeature'])

                    del dd['ProductFeature']

                if dd.get('ProductRelated'):
                    def sub(x):
                        if x['Product']['@ID'] not in DETECTED_PRODUCTS:
                            DETECTED_PRODUCTS[x['Product']['@ID']] = (
                                x['@Category_ID'], x['Product']['@ID'], x['Product']['@Prod_id'],
                                x['Product']['@Name'])
                            #PRODUCT_RELATED[product_id].add(x['Product']['@ID'])
                            print('|'.join([product_id, x['Product']['@ID']]), file=icecat_related)

                    if type(dd['ProductRelated']) == list:
                        for x in dd['ProductRelated']:
                            sub(x)
                    else:
                        sub(dd['ProductRelated'])

                    del dd['ProductRelated']

                if dd.get('ProductGallery') and dd['ProductGallery'].get('ProductPicture'):
                    def sub(x):
                        if x.get('@Original'):
                            #PRODUCT_IMAGES[product_id].add(x.get('@Original'))
                            print('|'.join([product_id, x.get('@Original')]), file=icecat_images)
                    if type(dd['ProductGallery'].get('ProductPicture')) == list:
                        for x in dd['ProductGallery'].get('ProductPicture'):
                            sub(x)
                    else:
                        sub(dd['ProductGallery'].get('ProductPicture'))

                    del dd['ProductGallery']

                outputfn = respath + '{}.txt'.format(product_id)
                with open(outputfn, 'w', encoding='utf-8') as output:
                    pprint.pprint(dd, stream=output, width=1000)

        if ver == 1:
            with open ('data/icecat.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                for r in reader:
                    if r[0]=='1':
                        full_filename = os.path.join('icecat_download/by_partno/', r[2])
                    elif r[0]=='2':
                        full_filename = os.path.join('icecat_download/by_name/', r[2])
                    elif r[0]=='3':
                        full_filename = os.path.join('icecat_download/by_name2/', r[2])
                    process_file(full_filename)

            for f in os.listdir('icecat_download/by_id_ru/'):
                fullpath = os.path.join('icecat_download/by_id_ru/', f)
                if os.path.isfile(fullpath):
                    try:
                        process_file(fullpath)
                    except Exception as e:
                        print('{} failed: {}'.format(fullpath, e))

                fullpath = os.path.join('icecat_download/by_id_en/', f)
                if os.path.isfile(fullpath):
                    try:
                        process_file(fullpath)
                    except Exception as e:
                        print('{} failed: {}'.format(fullpath, e))

        if ver == 2:
            skip = False
            for f in os.listdir(srcpath):
                if skip:
                    if f == '12568472.xml':
                        skip = False
                    else:
                        continue
                fullpath = os.path.join(srcpath, f)
                if os.path.isfile(fullpath):
                    process_file(fullpath)
                    # try:
                    #     process_file(fullpath)
                    # except Exception as e:
                    #     print('{} failed: {} {}'.format(fullpath, e, e.__traceback__))
                    #     exit()


        with open(path + 'result-categories.csv', 'w', encoding='utf-8') as output:
            for x in CATEGORIES:
                print(x, CATEGORIES[x], file=output, sep='|')

        with open(path + 'result-measures.csv', 'w', encoding='utf-8') as output:
            for x in MEASURES:
                print(x, MEASURES[x], file=output, sep='|')

        with open(path + 'result-local_measures.csv', 'w', encoding='utf-8') as output:
            for x in LOCAL_MEASURES:
                print(x, LOCAL_MEASURES[x], file=output, sep='|')


        with open(path + 'result-feature_groups.csv', 'w', encoding='utf-8') as output:
            for x in FEATURE_GROUPS:
                print(x, FEATURE_GROUPS[x], file=output, sep='|')

        with open(path + 'result-category_feature_groups__by_id.csv', 'w', encoding='utf-8') as output:
            for x in CATEGORY_FEATURE_GROUPS__BY_ID:
                print(x, *CATEGORY_FEATURE_GROUPS__BY_ID[x], file=output, sep='|')

        with open(path + 'result-features.csv', 'w', encoding='utf-8') as output:
            for x in FEATURES:
                print(x, *FEATURES[x], file=output, sep='|')

        with open(path + 'result-suppliers.csv', 'w', encoding='utf-8') as output:
            for x in SUPPLIERS:
                print(x, SUPPLIERS[x], file=output, sep='|')

        with open(path + 'parsed.csv', 'w', encoding='utf-8') as file:
            print(*list(set(PRODUCT_FEATURES)), file=file, sep='\n')

        with open(path + 'detected.csv', 'w', encoding='utf-8') as file:
            for x in DETECTED_PRODUCTS:
                if DETECTED_PRODUCTS[x][0] not in IGNORED_CATEGORIES:
                    print(*[x.replace('|', ';') for x in DETECTED_PRODUCTS[x]], sep='|', file=file)

    def load_more_files(self, *args, **options):

        print(options['start'], options['end'])
        try:
            start = int(options['start'])
            end = int(options['end'])
        except:
            print("bad params")
            exit(0)

        session = requests.session()

        PARSED = set()
        with open('data/parsed.csv', 'r', encoding='utf-8') as file:
            for x in file.readlines():
                y = x.strip()
                PARSED.add(y)

        with open('data/detected.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='|')
            for i, x  in enumerate(reader):
                if start>i or i>end:
                    continue
                if x[1] in PARSED:
                    continue
                filename = '{}.xml'.format(x[1])
                if os.path.exists(os.path.join('icecat_download/by_id_ru/', filename)):
                    continue
                if os.path.exists(os.path.join('icecat_download/by_id_no_ru/', filename)):
                    continue
                print(i, x[1])
                url = 'https://data.icecat.biz/xml_s3/xml_server3.cgi?product_id={};lang=ru;output=productxml'.format(x[1])
                res = session.get(url, auth=HTTPBasicAuth(login, password))
                if res.status_code == 200:
                    if len(res.text) >1000:
                        with open(os.path.join('icecat_download/by_id_ru/', filename), 'w', encoding='utf-8') as file:
                            print(res.text, file=file)
                    else:
                        with open(os.path.join('icecat_download/by_id_no_ru/', filename), 'w', encoding='utf-8') as file:
                            print(res.text, file=file)
                else:
                    print('FAIL id=[{}]'.format(x[1]))

    def categories_tree(self):
        with open('data/CategoriesList.xml', 'r', encoding='utf-8') as file:
            with open('categories.txt', 'w', encoding='utf-8') as output:
                s = file.read()
                print('Fileread OK')
                d = xmltodict.parse(s)
                print('Parsed OK')
                dd = d['ICECAT-interface']['Response']['CategoriesList']['Category']
                print('categories=',len(dd),type(dd))
                for d in dd:
                    name_en, name_ru, descr_en, descr_ru = '','','',''
                    if d.get('Name'):
                        if type(d.get('Name')) == list:
                            for name in d.get('Name'):
                                if name['@langid'] == '1': name_en = name['@Value']
                                if name['@langid'] == '8': name_ru = name['@Value']
                        else:
                            name = d.get('Name')
                            if name['@langid'] == '1': name_en = name['@Value']
                            if name['@langid'] == '8': name_ru = name['@Value']
                    if d.get('Description'):
                        if type(d.get('Description')) == list:
                            for descr in d.get('Description'):
                                if descr['@langid'] == '1': descr_en = name['@Value']
                                if descr['@langid'] == '8': descr_ru = name['@Value']
                        else:
                            descr = d.get('Description')
                            if descr['@langid'] == '1': descr_en = name['@Value']
                            if descr['@langid'] == '8': descr_ru = name['@Value']

                    print(d['@ID'], d['@LowPic'], d['ParentCategory']['@ID'], name_en, name_ru, descr_en, descr_ru,
                          sep='|', file=output)

    def process_files_printstore(self):
        def process_file(full_filename):
            with open('data/icecat_printstore.csv', 'a', encoding='utf-8') as icecat_printstore:
                with open(full_filename, 'r', encoding='utf-8') as file:
                    s = file.read()
                    d = xmltodict.parse(s)
                    dd = d['ICECAT-interface']['Product']
                    category_id = dd['Category']['@ID']
                    product_id = dd['@ID']
                    print('|'.join([*r, category_id, product_id]), file=icecat_printstore)
        with open ('data/icecat.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for r in reader:
                if r[0]=='1':
                    full_filename = os.path.join('icecat_download/by_partno/', r[2])
                elif r[0]=='2':
                    full_filename = os.path.join('icecat_download/by_name/', r[2])
                elif r[0]=='3':
                    full_filename = os.path.join('icecat_download/by_name2/', r[2])
                process_file(full_filename)

    def handle(self, *args, **options):
        #self.load_more_files(self, *args, **options)
        #self.load_from_ids(ICECATIDS)
        #self.process_files_printstore()
        self.process_files(2)

    # def add_arguments(self, parser):
    #     parser.add_argument('start')
    #     parser.add_argument('end')


from datetime import datetime

bdate = datetime.now()
bdate = '{}.{} {}:{}'.format(str(bdate.year%100), str(bdate.month), str(bdate.hour), str(bdate.minute))
