from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import *
from transliterate import slugify
import csv
from random import randint

TEST_LIMIT = 1000000

class Command(BaseCommand):
    help = "Database seeding"

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    BRANDS = [
        (1, 'HP'),
        (2, 'Brother'),
        (3, 'Canon'),
        (4, 'Dell'),
        (5, 'Epson'),
        (6, 'Xerox'),
        (7, 'Samsung'),
        (8, 'Ricoh'),
        (9, 'Panasonic'),
        (10, 'Lexmark'),
        (11, 'Konica Minolta'),
        (12, 'GCC Technologies'),
        (13, 'Kyocera'),
        (14, 'OKI'),
        (15, 'Nashuatec'),
        (16, 'MB'),
        (17, 'Citizen '),
        (18, 'Sharp'),
        (19, 'Toshiba'),
        (20, 'BZB'),
        (21, 'Develop'),
    ]

    PRINTER_TYPE_AV = [
        (1, 'лазерный'),
        (2, 'струйный'),
        (3, 'матричный'),
        (4, 'лазерный цветной'),
        (5, 'струйный цветной'),
        (6, 'термо'),
        (7, 'твердочернильный'),
        (8, 'твердочернильный цветной'),
    ]

    PAPER_FORMAT_AV = [
        (1, 'A0'),
        (2, 'A1'),
        (3, 'A2'),
        (4, 'A3'),
        (5, 'A4'),
        (6, 'A5'),
        (7, 'A6'),
        (8, 'Labels'),
    ]

    CARTRIDGE_COLOR_AV = [
        (1, 'цветной', 'color', 2),
        (2, 'черный', 'black', 0),
        (3, 'голубой', 'cyan', 3),
        (4, 'пурпурный', 'magenta', 5),
        (5, 'желтый', 'yellow', 4),
        (6, 'черный матовый', 'matte black', 11),
        (7, 'серый', 'light black', 9),
        (8, 'светло-голубой', 'light cyan', 6),
        (9, 'светло-пурпурный', 'light magenta', 7),
        (10, 'синий', 'blue', 13),
        (11, 'красный', 'red', 14),
        (12, 'глянец', 'gloss', 15),
        (13, 'светло-серый', 'light light black', 8),
        (14, 'фото', 'photo', 16),
        (15, 'флуоресцентный', 'fluorescent', 17),
        (16, 'черный фото', 'photo black', 12),
        (17, 'зеленый', 'green', 18),
        (18, 'оранжевый', 'orange', 19),
        (19, 'хроматический красный', 'chromatic red', 20),
        (20, 'скрепки', 'staple', 22),
        (21, 'белый', 'white', 24),
        (22, 'прозрачный', 'transparent', 22),
        (23, 'неоновый', 'neon', 23),
        (24, 'темно-серый', 'dark gray', 10),
    ]

    CARTRIDGE_TYPE_AV = [
        (1, 'Картридж'),
        (2, 'Тонер'),
        (3, 'Девелопер'),
        (4, 'Чернила'),
        (5, 'Фотобарабан'),
        (6, 'Емк. для отраб.'),
        (7, 'Печ. головка'),
        (8, 'Блок термозакрепления'),
        (9, 'Блок переноса изобр.'),
        (11, 'Твердые чернила'),
        (12, 'Вал переноса изображения'),
        (13, 'Озоновый фильтр'),
        (14, 'Блок проявки'),
    ]

    CATEGORIES = [
        (1, 'Принтер'),
        (2, 'Плоттер'),
        (3, 'Факс'),
        (4, 'Копир'),
        (5, 'МФУ'),
        (6, 'Системный блок'),
        (7, 'Ноутбук'),
        (8, 'Монитор'),
        (9, 'ИБП'),
        (10, 'Сканер'),
        (11, 'Коммутатор'),
        (12, 'Маршрутизатор'),
        (13, 'Телефон'),
        (14, 'Точка доступа'),
        (15, 'Принт-сервер'),
        (16, 'Клавиатура'),
        (17, 'Мышь'),
        (18, 'Кассовый аппарат'),
    ]

    SLOTS = [
        (1, 1, 'Cartridge Black', 'Картридж, Тонер, Чернила', 'черный'),
        (2, 2, 'Cartridge Cyan', 'Картридж, Тонер, Чернила', 'голубой'),
        (3, 3, 'Cartridge Yellow', 'Картридж, Тонер, Чернила', 'желтый'),
        (4, 4, 'Cartridge Magenta', 'Картридж, Тонер, Чернила', 'пурпурный'),
        (14, 5, 'Cartridge Light Cyan', 'Картридж, Тонер, Чернила', 'светло-голубой'),
        (15, 6, 'Cartridge Light Magenta', 'Картридж, Тонер, Чернила', 'светло-пурпурный'),
        (5, 7, 'Cartridge Color', 'Картридж', 'цветной'),
        (21, 8, 'Cartridge Black & Fluorescent', 'Картридж', 'черный, флуоресцентный'),
        (22, 9, 'Cartridge Color & Photo', 'Картридж', 'цветной, фото'),
        (23, 10, 'Cartridge Black & Photo', 'Картридж', 'черный, фото'),
        (33, 11, 'Cartridge Black Photo', 'Картридж, Тонер, Чернила', 'черный фото'),
        (32, 12, 'Cartridge Photo', 'Картридж, Тонер, Чернила', 'фото'),
        (35, 13, 'Cartridge Black & Matte', 'Картридж, Тонер, Чернила', 'черный, черный матовый'),
        (36, 14, 'Cartridge Black Matte', 'Картридж, Тонер, Чернила', 'черный матовый'),
        (30, 15, 'Cartridge Gray', 'Картридж, Тонер, Чернила', 'серый'),
        (31, 16, 'Cartridge Light Gray', 'Картридж, Тонер, Чернила', 'светло-серый'),
        (48, 17, 'Cartridge Dark Gray', 'Картридж, Тонер, Чернила', '* темно-серый'),
        (39, 18, 'Cartridge Red', 'Картридж, Тонер, Чернила', 'красный'),
        (34, 19, 'Cartridge Green', 'Картридж, Тонер, Чернила', 'зеленый'),
        (37, 20, 'Cartridge Blue', 'Картридж, Тонер, Чернила', 'синий'),
        (38, 21, 'Cartridge Glossy', 'Картридж, Тонер, Чернила', 'глянец'),
        (45, 22, 'Cartridge White', 'Картридж, Тонер, Чернила', 'белый'),
        (46, 23, 'Cartridge Transparent', 'Картридж, Тонер, Чернила', 'прозрачный'),
        (47, 24, 'Cartridge Neon', 'Картридж, Тонер, Чернила', 'неоновый'),
        (7, 25, 'Printhead Black', 'Печ. головка', 'черный'),
        (8, 26, 'Printhead Cyan', 'Печ. головка', 'голубой'),
        (9, 27, 'Printhead Yellow', 'Печ. головка', 'желтый'),
        (10, 28, 'Printhead Magenta', 'Печ. головка', 'пурпурный'),
        (11, 29, 'Printhead Light Cyan', 'Печ. головка', 'светло-голубой'),
        (12, 30, 'Printhead Light Magenta', 'Печ. головка', 'светло-пурпурный'),
        (13, 31, 'Printhead Color', 'Печ. головка', 'цветной'),
        (16, 32, 'Drum Black', 'Барабан, Фотокондуктор', 'черный'),
        (17, 33, 'Drum Cyan', 'Барабан, Фотокондуктор', 'голубой'),
        (18, 34, 'Drum Yellow', 'Барабан, Фотокондуктор', 'желтый'),
        (19, 35, 'Drum Magenta', 'Барабан, Фотокондуктор', 'пурпурный'),
        (20, 36, 'Drum Color', 'Барабан, Фотокондуктор', 'цветной'),
        (24, 37, 'Developer Black', 'Девелопер', 'черный'),
        (25, 38, 'Developer Cyan', 'Девелопер', 'голубой'),
        (26, 39, 'Developer Yellow', 'Девелопер', 'желтый'),
        (27, 40, 'Developer Magenta', 'Девелопер', 'пурпурный'),
        (28, 41, 'Fuser', 'Блок термозакрепления', 'Все цвета РМ'),
        (29, 42, 'Transfer Unit', 'Блок переноса изобр.', 'Все цвета РМ'),
        (41, 43, 'Transfer Unit Black', 'Блок переноса изобр.', 'черный'),
        (42, 44, 'Transfer Unit Cyan', 'Блок переноса изобр.', 'голубой'),
        (44, 45, 'Transfer Unit Yellow', 'Блок переноса изобр.', 'желтый'),
        (43, 46, 'Transfer Unit Magenta', 'Блок переноса изобр.', 'пурпурный'),
        (6, 47, 'Waste tank', 'Емк. для отраб.', 'Все цвета РМ'),
        (40, 48, 'Staples', 'Картридж', 'скрепки'),
    ]

    SLOT_TYPES = [
        'Барабан, Фотокондуктор',
        'Блок переноса изобр.',
        'Блок термозакрепления',
        'Девелопер',
        'Емк. для отраб.',
        'Картридж',
        'Картридж, Тонер, Чернила',
        'Печ. головка',
    ]

    SLOT_COLORS = [
        '* темно-серый',
        'Все цвета РМ',
        'белый',
        'глянец',
        'голубой',
        'желтый',
        'зеленый',
        'красный',
        'неоновый',
        'прозрачный',
        'пурпурный',
        'светло-голубой',
        'светло-пурпурный',
        'светло-серый',
        'серый',
        'синий',
        'скрепки',
        'фото',
        'цветной',
        'цветной, фото',
        'черный',
        'черный матовый',
        'черный фото',
        'черный, флуоресцентный',
        'черный, фото',
        'черный, черный матовый',
    ]

    BRANDS_DICT = {}
    PRINTER_TYPES_DICT = {}
    PAPER_FORMATS_DICT = {}
    CARTRIDGE_COLORS_DICT = {}
    CARTRIDGE_TYPES_DICT = {}
    CATEGORIES_DICT = {}
    CARTRIDGE_CATEGORIES_DICT = {}
    PRODUCTS_DICT = {}
    SLUGS_DICT = {}
    SLOTS_DICT = {}
    SLOT_COLORS_DICT = {}
    SLOT_TYPES_DICT = {}

    def handle(self, *args, **options):

        user = User.objects.create(first_name='Han', last_name='Solo', email='as@solotony.com', username='admin',
                                   is_active=True, is_superuser=True, is_staff=True)
        user.set_password('admin')
        user.save()

        printer_type = ProductAttribute.objects.create(name='Тип печати', type=ProductAttribute.TYPE_ENUM, slug=slugify('Тип печати', 'ru'))
        paper_format = ProductAttribute.objects.create(name='Формат бумаги', type=ProductAttribute.TYPE_ENUM, slug=slugify('Формат бумаги', 'ru'))
        colors_count = ProductAttribute.objects.create(name='Количество цветов', type=ProductAttribute.TYPE_INTEGER, slug=slugify('Количество цветов', 'ru'))
        no_border = ProductAttribute.objects.create(name='No Border', type=ProductAttribute.TYPE_BOOLEAN, slug=slugify('No Border', 'ru'))
        barcode = ProductAttribute.objects.create(name='Штрих код', type=ProductAttribute.TYPE_STRING, slug=slugify('Штрих код', 'ru'))
        ident_oid = ProductAttribute.objects.create(name='IdentOID', type=ProductAttribute.TYPE_STRING, slug=slugify('IdentOID', 'ru'))
        ident_value = ProductAttribute.objects.create(name='IdentValue', type=ProductAttribute.TYPE_STRING, slug=slugify('IdentValue', 'ru'))
        firmware = ProductAttribute.objects.create(name='Firmware', type=ProductAttribute.TYPE_STRING, slug=slugify('Firmware', 'ru'))
        fav_cartrige_ids = ProductAttribute.objects.create(name='FavCartrigeIDs', type=ProductAttribute.TYPE_STRING, slug=slugify('FavCartrigeIDs', 'ru'))

        colors_string = ProductAttribute.objects.create(name='ColorsString', type=ProductAttribute.TYPE_STRING, slug=slugify('ColorsString', 'ru'))
        roll_support = ProductAttribute.objects.create(name='RollSupport', type=ProductAttribute.TYPE_BOOLEAN, slug=slugify('RollSupport', 'ru'))

        device_attributes = [printer_type, paper_format, colors_count, no_border, barcode, ident_oid,
                             ident_value, firmware, fav_cartrige_ids]

        cartridge_type = ProductAttribute.objects.create(name='Вид расходника', type=ProductAttribute.TYPE_ENUM, slug=slugify('Вид расходника', 'ru'))
        resourse = ProductAttribute.objects.create(name='Ресурс картриджа', type=ProductAttribute.TYPE_INTEGER, slug=slugify('Ресурс картриджа', 'ru'))
        items_in_pack = ProductAttribute.objects.create(name='Количество в упаковке', type=ProductAttribute.TYPE_INTEGER, slug=slugify('Количество в упаковке', 'ru'))
        cartridge_color = ProductAttribute.objects.create(name='Цвет картриджа', type=ProductAttribute.TYPE_ENUM, slug=slugify('Цвет картриджа', 'ru'))
        compability = ProductAttribute.objects.create(name='Совместимость', type=ProductAttribute.TYPE_STRING, slug=slugify('Совместимость', 'ru'))

        maxwriteoffspeed = ProductAttribute.objects.create(name='MaxWriteOffSpeed', type=ProductAttribute.TYPE_INTEGER, slug=slugify('MaxWriteOffSpeed', 'ru'))
        avgwriteoffspeed = ProductAttribute.objects.create(name='AvgWriteOffSpeed', type=ProductAttribute.TYPE_INTEGER, slug=slugify('AvgWriteOffSpeed', 'ru'))
        lastwriteoffdate = ProductAttribute.objects.create(name='LastWriteOffDate', type=ProductAttribute.TYPE_INTEGER, slug=slugify('LastWriteOffDate', 'ru'))
        lastwriteoffquantity = ProductAttribute.objects.create(name='LastWriteOffQuantity', type=ProductAttribute.TYPE_INTEGER, slug=slugify('LastWriteOffQuantity', 'ru'))
        sumquantity = ProductAttribute.objects.create(name='SumQuantity', type=ProductAttribute.TYPE_INTEGER, slug=slugify('SumQuantity', 'ru'))
        goodsnumber = ProductAttribute.objects.create(name='GoodsNumber', type=ProductAttribute.TYPE_INTEGER, slug=slugify('GoodsNumber', 'ru'))

        expendable_attributes = [resourse, items_in_pack, cartridge_type, cartridge_color, compability]

        for b in self.BRANDS:
            self.BRANDS_DICT[b[0]] = Brand.objects.create(name=b[1], slug=slugify(b[1], language_code='ru'))

        for v in self.PAPER_FORMAT_AV:
            self.PAPER_FORMATS_DICT[v[0]] = ProductAttributeChoice.objects.create(attribute=paper_format, value=v[1])

        for v in self.PRINTER_TYPE_AV:
            self.PRINTER_TYPES_DICT[v[0]] = ProductAttributeChoice.objects.create(attribute=printer_type, value=v[1])

        for v in self.CARTRIDGE_COLOR_AV:
            self.CARTRIDGE_COLORS_DICT[v[0]] = ProductAttributeChoice.objects.create(attribute=cartridge_color, value=v[1],
                                                                              order=v[3])
        for v in self.CARTRIDGE_TYPE_AV:
            self.CARTRIDGE_TYPES_DICT[v[0]] = ProductAttributeChoice.objects.create(attribute=cartridge_type, value=v[1])

        devices_cat = Category.objects.create(name='Устройства', slug=slugify('Устройства', 'ru'))
        expendable_cat = Category.objects.create(name='Расходные материалы', slug=slugify('Расходные материалы', 'ru'))

        devices_cat.attributes.add(*device_attributes)
        expendable_cat.attributes.add(*expendable_attributes)

        for v in self.CATEGORIES:
            self.CATEGORIES_DICT[v[0]] = Category.objects.create(name=v[1], slug=slugify(v[1], 'ru'), parent=devices_cat)
            self.CATEGORIES_DICT[v[0]].attributes.add(*device_attributes)

        for v in self.CARTRIDGE_TYPE_AV:
            self.CARTRIDGE_CATEGORIES_DICT[v[0]] = Category.objects.create(name=v[1], slug=slugify(v[1], 'ru'),
                                                                           parent=expendable_cat)
            self.CARTRIDGE_CATEGORIES_DICT[v[0]].attributes.add(*expendable_attributes)

        slot_type = SlotAttribute.objects.create(name='Тип', type=SlotAttribute.TYPE_ENUM, slug=slugify('Тип', 'ru'))
        slot_color = SlotAttribute.objects.create(name='Цвет', type=SlotAttribute.TYPE_ENUM, slug=slugify('Цвет', 'ru'))

        for v in self.SLOT_TYPES:
            self.SLOT_TYPES_DICT[v] = SlotAttributeChoice.objects.create(attribute=slot_type, value=v)

        for v in self.SLOT_COLORS:
            self.SLOT_COLORS_DICT[v] = SlotAttributeChoice.objects.create(attribute=slot_color, value=v)

        for v in self.SLOTS:
            self.SLOTS_DICT[v[0]] = Slot.objects.create(name=v[2], printstore_id=v[0], order=v[1])
            _slot_color = self.SLOT_COLORS_DICT[v[4]]
            _slot_type = self.SLOT_TYPES_DICT[v[3]]
            SlotAttributeValue.objects.bulk_create([
                SlotAttributeValue(slot=self.SLOTS_DICT[v[0]], attribute=slot_color, int_value=_slot_color.id),
                SlotAttributeValue(slot=self.SLOTS_DICT[v[0]], attribute=slot_type, int_value=_slot_type.id)
            ])

        with open('data/models.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            counter = 0
            for r in reader:
                if counter > TEST_LIMIT: break
                counter += 1
                # ['ID', 'VendorID', 'FormatID', 'PrintTypeID', 'ModelTypeID', 'Name',
                # 'ColorsCount', 'ColorsString', 'RollSupport', 'PartNumber', 'NoBorder',
                # 'Added', 'Updated', 'Description', 'UserUpdated', 'FavCartrigeIDs',
                # 'Barcode', 'ProfileID', 'IdentOID', 'IdentValue', 'Photo', 'Firmware']

                _brand, _paper_format, _category, _printer_type, _name, _part_num, _slug, _profile_id = \
                    None, None, None, None, None, None, None, None

                if int(r['VendorID']) in self.BRANDS_DICT:
                    _brand = self.BRANDS_DICT[int(r['VendorID'])]

                if int(r['ModelTypeID']) in self.CATEGORIES_DICT:
                    _category = self.CATEGORIES_DICT[int(r['ModelTypeID'])]

                if int(r['FormatID']) in self.PAPER_FORMATS_DICT:
                    _paper_format = self.PAPER_FORMATS_DICT[int(r['FormatID'])].id

                if int(r['PrintTypeID']) in self.PRINTER_TYPES_DICT:
                    _printer_type = self.PRINTER_TYPES_DICT[int(r['PrintTypeID'])].id

                if r['PartNumber'].strip():
                    _part_num = r['PartNumber'].strip()
                    _slug = _part_num

                if r['Name'].strip():
                    _name = r['Name'].strip()
                    if _slug:
                        _slug += ' ' + _name
                    else:
                        _slug = _name

                _oslug = _slug = slugify(_slug, 'ru')
                while (_brand.id, _slug) in self.SLUGS_DICT:
                    _slug = _oslug + str(randint(0, 999999999))

                _printstore_id = int(r['ID'])
                _profile_id = None

                try:
                    _profile_id = int(r['ProfileID'])
                except:
                    pass

                _colors_count = int(r['ColorsCount'])
                _no_border = r['NoBorder'] == 'ИСТИНА'
                _barcode = r['Barcode'].strip()

                _ident_oid = r['IdentOID'].strip()
                _ident_value = r['IdentValue'].strip()
                _firmware = r['Firmware'].strip()
                _fav_cartrige_ids = r['FavCartrigeIDs'].strip()

                _description = None
                if r['Description'].strip():
                    _description = r['Description'].strip()

                product = Product.objects.create(
                    name=_name,
                    slug=_slug,
                    profile_id=_profile_id,
                    printstore_id=_printstore_id,
                    part_num=_part_num,
                    brand=_brand,
                    category=_category,
                    description=_description
                )

                self.PRODUCTS_DICT[('p', _printstore_id)] = product
                self.SLUGS_DICT[(_brand.id, _slug)] = product

                attributes = []

                if _printer_type:
                    attributes.append(ProductAttributeValue(attribute=printer_type, product=product, int_value=_printer_type))

                if _paper_format:
                    attributes.append(ProductAttributeValue(attribute=paper_format, product=product, int_value=_paper_format))

                if _colors_count:
                    attributes.append(ProductAttributeValue(attribute=colors_count, product=product, int_value=_colors_count))

                if _no_border:
                    attributes.append(ProductAttributeValue(attribute=no_border, product=product, int_value=_no_border))

                if _barcode:
                    attributes.append(ProductAttributeValue(attribute=barcode, product=product, str_value=_barcode))

                if _ident_oid:
                    attributes.append(ProductAttributeValue(attribute=ident_oid, product=product, str_value=_ident_oid))

                if _ident_value:
                    attributes.append(ProductAttributeValue(attribute=ident_value, product=product, str_value=_ident_value))

                if _firmware:
                    attributes.append(ProductAttributeValue(attribute=firmware, product=product, str_value=_firmware))

                if _fav_cartrige_ids:
                    attributes.append(
                        ProductAttributeValue(attribute=fav_cartrige_ids, product=product, str_value=_fav_cartrige_ids))

                ProductAttributeValue.objects.bulk_create(attributes)

        with open('data/cartridges.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            counter = 0
            for r in reader:
                if counter > TEST_LIMIT: break
                counter +=1
                # ID,VendorID,CartrigeTypeID,Name,NameLocal,PartNumber,Resourse,ItemsInPack,CartrigeColorID,
                # Added,Updated, Description,MaxWriteOffSpeed,AvgWriteOffSpeed,UserUpdated,LastWriteOffDate,
                # LastWriteOffQuantity,SumQuantity, GoodsNumber,LocalName,ReportName,ShowInNeedToBuy,Barcode,Hidden

                _brand, _category, _cartridge_type, _name, _part_num, _slug, _profile_id, _cartridge_color_id = \
                    None, None, None, None, None, None, None, None

                if int(r['VendorID']) in self.BRANDS_DICT:
                    _brand = self.BRANDS_DICT[int(r['VendorID'])]

                if int(r['CartrigeTypeID']) in self.CARTRIDGE_TYPES_DICT:
                    _cartridge_type = self.CARTRIDGE_TYPES_DICT[int(r['CartrigeTypeID'])].id

                if int(r['CartrigeTypeID']) in self.CARTRIDGE_CATEGORIES_DICT:
                    _category = self.CARTRIDGE_CATEGORIES_DICT[int(r['CartrigeTypeID'])]

                if int(r['CartrigeColorID']) in self.CARTRIDGE_COLORS_DICT:
                    _cartridge_color_id = self.CARTRIDGE_COLORS_DICT[int(r['CartrigeColorID'])].id

                if r['PartNumber'].strip():
                    _part_num = r['PartNumber'].strip()
                    _slug = _part_num

                if r['Name'].strip():
                    _name = r['Name'].strip()
                    if _slug:
                        _slug += ' ' + _name
                    else:
                        _slug = _name

                _oslug = _slug = slugify(_slug, 'ru')
                while (_brand.id, _slug) in self.SLUGS_DICT:
                    _slug = _oslug + str(randint(0, 999999999))

                _description = None
                if r['Description'].strip():
                    _description = r['Description'].strip()

                _printstore_id = int(r['ID'])

                # ,,,,NameLocal,,,,,
                # ,, ,,,,,
                # ,SumQuantity, GoodsNumber,,,ShowInNeedToBuy,,Hidden

                _resourse = int(r['Resourse'])
                _items_in_pack = int(r['ItemsInPack'])
                _compability = r['Name'].strip()

                try:
                    product = Product.objects.create(
                        name=_name,
                        slug=_slug,
                        printstore_id=_printstore_id,
                        part_num=_part_num,
                        brand=_brand,
                        category=_category,
                        description=_description
                    )
                except Exception as e:
                    print(e, "id={} pn={} vendor={} name_len={}".format(r['ID'], r['PartNumber'], r['VendorID'], len(_name)))
                    continue

                attributes = []

                if _cartridge_type:
                    attributes.append(ProductAttributeValue(attribute=cartridge_type, product=product, int_value=_cartridge_type))

                if _barcode:
                    attributes.append(ProductAttributeValue(attribute=barcode, product=product, str_value=_barcode))

                if _resourse:
                    attributes.append(ProductAttributeValue(attribute=resourse, product=product, int_value=_resourse))

                if _items_in_pack:
                    attributes.append(ProductAttributeValue(attribute=items_in_pack, product=product, int_value=_items_in_pack))

                if _cartridge_color_id:
                    attributes.append(ProductAttributeValue(attribute=cartridge_color, product=product, int_value=_cartridge_color_id))

                if _compability:
                    attributes.append(ProductAttributeValue(attribute=compability, product=product, str_value=_compability))

                ProductAttributeValue.objects.bulk_create(attributes)

                self.PRODUCTS_DICT[('c', _printstore_id)] = product
                self.SLUGS_DICT[(_brand.id, _slug)] = product
            pass


        with open('data/compabilities.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            relations = []
            for r in reader:
                if r['SlotID'].strip():
                    slot_id = int(r['SlotID'].strip())
                else:
                    slot_id = None
                cartridge_id = int(r['CartrigeID'])
                model_id = int(r['ModelID'])

                if slot_id not in self.SLOTS_DICT:
                    _slot = None
                else:
                    _slot = self.SLOTS_DICT[slot_id]


                if ('c', cartridge_id) not in self.PRODUCTS_DICT:
                    print('CARTRIDGE [{}] FAILED'.format(cartridge_id))
                    continue
                _product_related = self.PRODUCTS_DICT[('c', cartridge_id)]

                if ('p', model_id) not in self.PRODUCTS_DICT:
                    print('PRINTER [{}] FAILED'.format(model_id))
                    continue
                _product_base = self.PRODUCTS_DICT[('p', model_id)]

                relations.append(ProductToProduct(
                    product_base=_product_base,
                    product_related=_product_related,
                    slot=_slot
                ))
            ProductToProduct.objects.bulk_create(relations)
        return