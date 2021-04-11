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
import os
from django.conf import settings

re_image = re.compile(r'^image_(\d+)\.jpg$')

class Command(BaseCommand):
    help = "Database seeding"

    def handle(self, *args, **options):

        FILES = {}

        for path, dirs, files in os.walk(os.path.join('media', 'images')):
            for file in files:
                mo = re_image.match(file)
                if mo:
                    id = int(mo[1])
                    print(id, os.path.join(path[6:], file))
                    FILES[id] = os.path.join(path[6:], file)


        images = ProductImage.objects_all.exclude(external__isnull=True).all()

        images_to_update = []

        for image in images:
            print('image {}'.format(image.id))
            if image.id in FILES:
                #image.image.path = FILES[image.id]

                image.image = image.image.field.attr_class(image, image.image.field, FILES[image.id])

                image.save()

