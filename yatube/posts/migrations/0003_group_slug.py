# Generated by Django 2.2.19 on 2023-01-06 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20230106_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
    ]
