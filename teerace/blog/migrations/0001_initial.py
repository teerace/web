# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('published_at', models.DateTimeField(auto_now=True)),
                ('enable_comments', models.BooleanField(default=True)),
                ('is_micro', models.BooleanField(default=False, help_text=b'Designates whether this entry should be displayed as micropost. It will not be included in Teeplanet feed.', verbose_name=b'micro')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.CharField(max_length=100, blank=True)),
                ('excerpt', models.TextField(help_text=b'You may use Markdown syntax', blank=True)),
                ('excerpt_html', models.TextField(blank=True)),
                ('content', models.TextField(help_text=b'You may use Markdown syntax')),
                ('content_html', models.TextField()),
                ('status', models.IntegerField(default=2, choices=[(1, b'Published'), (2, b'Draft'), (3, b'Hidden')])),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'get_latest_by': 'created_at',
                'verbose_name_plural': 'Entries',
            },
        ),
    ]
