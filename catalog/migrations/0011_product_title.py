# Generated by Django 3.1 on 2020-09-04 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_auto_20200904_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='title',
            field=models.CharField(blank=True, default=None, max_length=200, null=True, verbose_name='title'),
        ),
    ]
