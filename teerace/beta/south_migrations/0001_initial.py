# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BetaKey'
        db.create_table('beta_betakey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('is_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('beta', ['BetaKey'])


    def backwards(self, orm):
        
        # Deleting model 'BetaKey'
        db.delete_table('beta_betakey')


    models = {
        'beta.betakey': {
            'Meta': {'object_name': 'BetaKey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'})
        }
    }

    complete_apps = ['beta']
