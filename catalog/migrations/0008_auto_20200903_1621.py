# Generated by Django 3.1 on 2020-09-03 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_auto_20200903_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattribute',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='catalog.measureunit', verbose_name='measure unit'),
        ),
        migrations.AddField(
            model_name='slotattribute',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='catalog.measureunit', verbose_name='measure unit'),
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='childs', related_query_name='child', to='catalog.category', verbose_name='parent category'),
        ),
    ]
