# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IED'
        db.create_table('mara_ied', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('co_master', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.COMaster'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('rs485_address', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('mara', ['IED'])


    def backwards(self, orm):
        # Deleting model 'IED'
        db.delete_table('mara_ied')


    models = {
        'mara.comaster': {
            'Meta': {'object_name': 'COMaster'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'poll_interval': ('django.db.models.fields.FloatField', [], {'default': '5'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '9761'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'rs485_destination': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_source': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.ied': {
            'Meta': {'object_name': 'IED'},
            'co_master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.COMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_address': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'mara.profile': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Profile'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1'})
        }
    }

    complete_apps = ['mara']