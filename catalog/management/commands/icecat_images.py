from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import *
from transliterate import slugify
import csv
from random import randint
import requests
import logging
from django.core.files.base import ContentFile
from PIL import Image
import io
from threading import Thread
import time
from common.functions import get_upload_path

THREADS = 10

class Command(BaseCommand):
    help = "Database seeding"

    headers = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control':'max-age=0',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'none',
        'upgrade-insecure-requests':'1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.284',
    }

    types = [
        'image/bmp',
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif',
        'image/pjpeg'
    ]


    def handle(self, *args, **options):

        sess = requests.Session()
        sess.headers.update(self.headers)
        logger = logging.getLogger('commands')

        def process_image(image):
            nonlocal sess
            nonlocal logger
            print(image.external)
            if image.external:
                result = sess.get(image.external)
                if result.status_code != 200:
                    logger.error('response code {} at url {}'.format(result.status_code, image.external))
                    image.external = None
                    return
                if result.headers['Content-Type'] not in self.types:
                    logger.error('content-type {} at url {}'.format(result.headers['Content-Type'], image.external))
                    image.external = None
                    return
            else:
                image.external = None
                return
            try:
                img = Image.open(io.BytesIO(result.content))
                print(
                    'format={} img.mode={} size={} palette={}'.format(img.format, img.mode, img.size, img.palette))

                img.thumbnail((1000, 1000))
                bg = Image.new(mode='RGBA', size=img.size, color=(255, 255, 255, 255))
                #TODO похоже здесь ошибка если img не RGBA а RGB
                img = Image.alpha_composite(bg, img)
                #with io.BytesIO() as output:
                filename = get_upload_path('images','image_{}.jpg'.format(image.id))
                with open(filename, 'wb') as output:
                    img.convert("RGB").save(output, format='JPEG')
                    print('SAVE TO filename', filename)
                    # contents = output.getvalue()
                    # file = ContentFile(contents)
                    #
                    # #image.image.save(filename, file)
            except Exception as e:
                logger.error('image filed at url {} {}'.format(image.external, e))
                return

        start_at = time.time()
        finish = False
        images = ProductImage.objects.filter(image__isnull=True).exclude(external__isnull=True).all()
        it = iter(images)
        counter = 0
        while True:
            if finish:
                break
            threads = [None]*THREADS
            images = [None] * THREADS
            for i in range(THREADS):
                try:
                    images[i] = next(it)
                    threads[i] = Thread(target=process_image, args=(images[i],))
                    threads[i].start()
                except StopIteration as e:
                    finish = True
                    pass
            for i in range(THREADS):
                if threads[i] is not None:
                    threads[i].join()
                #images[i].save()
            counter += THREADS
            t = time.time() - start_at
            e = t / counter * (len(images)-counter)
            print('-- TIME USED: {}  ESTIMATED: {}'.format(t, e))