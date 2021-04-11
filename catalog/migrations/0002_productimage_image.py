# Generated by Django 3.1 on 2020-10-29 12:53

import common.functions
from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='image',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to=common.functions.get_upload_path, verbose_name='image'),
        ),
    ]