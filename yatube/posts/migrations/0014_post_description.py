# Generated by Django 2.2.16 on 2022-11-21 09:32

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20221119_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
