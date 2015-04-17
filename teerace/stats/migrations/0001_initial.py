# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('displayed_name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('slug', models.SlugField(unique=True, max_length=30)),
                ('data', picklefield.fields.PickledObjectField(null=True, editable=False)),
            ],
        ),
    ]
