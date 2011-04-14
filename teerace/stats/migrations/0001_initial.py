# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Chart'
        db.create_table('stats_chart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('displayed_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=30, db_index=True)),
            ('data', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal('stats', ['Chart'])


    def backwards(self, orm):
        
        # Deleting model 'Chart'
        db.delete_table('stats_chart')


    models = {
        'stats.chart': {
            'Meta': {'object_name': 'Chart'},
            'data': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'displayed_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'})
        }
    }

    complete_apps = ['stats']
