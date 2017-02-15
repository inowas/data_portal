# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-09 14:23
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('app', '0005_auto_20170209_0213'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
