# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 13:07
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NumValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RasValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', django.contrib.gis.db.models.fields.RasterField(null=True, srid=3857)),
            ],
        ),
        migrations.CreateModel(
            name='TSValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestart', models.DateTimeField(null=True)),
                ('interval', models.DurationField(null=True)),
                ('value', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(null=True), null=True, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='ValueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geom_type', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='value',
            name='prop',
        ),
        migrations.RemoveField(
            model_name='valueseries',
            name='prop',
        ),
        migrations.RemoveField(
            model_name='prop',
            name='is_series',
        ),
        migrations.AlterField(
            model_name='prop',
            name='model_object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='app.ModelObject'),
        ),
        migrations.AlterField(
            model_name='prop',
            name='property_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='app.PropertyType'),
        ),
        migrations.DeleteModel(
            name='Value',
        ),
        migrations.DeleteModel(
            name='ValueSeries',
        ),
        migrations.AddField(
            model_name='tsvalue',
            name='prop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ts_value', to='app.Prop'),
        ),
        migrations.AddField(
            model_name='rasvalue',
            name='prop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ras_values', to='app.Prop'),
        ),
        migrations.AddField(
            model_name='numvalue',
            name='prop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='num_values', to='app.Prop'),
        ),
        migrations.AddField(
            model_name='catvalue',
            name='prop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cat_values', to='app.Prop'),
        ),
        migrations.AddField(
            model_name='prop',
            name='value_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='properties', to='app.ValueType'),
        ),
    ]