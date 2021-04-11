from django.core.management.base import BaseCommand
from django.conf import settings
import os
import re

re_src = re.compile(r'(src|href)="[^"]*?static/([^"]*?)"', re.MULTILINE+re.DOTALL)

class Command(BaseCommand):
    help = "Post-webpack template process"
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'website/templates/layout')
        for f in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
            with open (os.path.join(path, f), 'r', encoding='utf=8') as file:
                content = file.read()

            content = re_src.sub(r'''\1="{% static '\2' %}"''', content)
            print(content)

            with open (os.path.join(path, f), 'w', encoding='utf=8') as file:
                print(content, file=file)
