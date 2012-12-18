# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'COMaster.enabled'
        db.add_column('mara_comaster', 'enabled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'COMaster.port'
        db.add_column('mara_comaster', 'port',
                      self.gf('django.db.models.fields.IntegerField')(default=9761),
                      keep_default=False)

        # Adding field 'COMaster.poll_interval'
        db.add_column('mara_comaster', 'poll_interval',
                      self.gf('django.db.models.fields.FloatField')(default=5),
                      keep_default=False)

        # Adding field 'COMaster.sequence'
        db.add_column('mara_comaster', 'sequence',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'COMaster.rs485_source'
        db.add_column('mara_comaster', 'rs485_source',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'COMaster.rs485_destination'
        db.add_column('mara_comaster', 'rs485_destination',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Profile.version'
        db.add_column('mara_profile', 'version',
                      self.gf('django.db.models.fields.CharField')(default='1', max_length=1),
                      keep_default=False)

        # Adding field 'Profile.date'
        db.add_column('mara_profile', 'date',
                      self.gf('django.db.models.fields.DateField')(auto_now=True, default=datetime.datetime(2012, 12, 17, 0, 0), blank=True),
                      keep_default=False)

        # Adding unique constraint on 'Profile', fields ['name']
        db.create_unique('mara_profile', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Profile', fields ['name']
        db.delete_unique('mara_profile', ['name'])

        # Deleting field 'COMaster.enabled'
        db.delete_column('mara_comaster', 'enabled')

        # Deleting field 'COMaster.port'
        db.delete_column('mara_comaster', 'port')

        # Deleting field 'COMaster.poll_interval'
        db.delete_column('mara_comaster', 'poll_interval')

        # Deleting field 'COMaster.sequence'
        db.delete_column('mara_comaster', 'sequence')

        # Deleting field 'COMaster.rs485_source'
        db.delete_column('mara_comaster', 'rs485_source')

        # Deleting field 'COMaster.rs485_destination'
        db.delete_column('mara_comaster', 'rs485_destination')

        # Deleting field 'Profile.version'
        db.delete_column('mara_profile', 'version')

        # Deleting field 'Profile.date'
        db.delete_column('mara_profile', 'date')


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