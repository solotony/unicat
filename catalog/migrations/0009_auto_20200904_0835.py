# Generated by Django 3.1 on 2020-09-04 05:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_auto_20200903_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='icecat_category_id',
            field=models.BigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat category id'),
        ),
        migrations.AlterField(
            model_name='attributegroup',
            name='icecat_id',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat id'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='icecat_id',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat id'),
        ),
        migrations.AlterField(
            model_name='category',
            name='icecat_id',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat id'),
        ),
        migrations.AlterField(
            model_name='measureunit',
            name='icecat_id',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat id'),
        ),
        migrations.AlterField(
            model_name='product',
            name='icecat_id',
            field=models.BigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat id'),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='icecat_id',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='icecat id'),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external', models.URLField(verbose_name='external image url')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', related_query_name='image', to='catalog.product')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
        ),
    ]