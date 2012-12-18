# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DI'
        db.create_table('mara_di', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('q', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mara', ['DI'])

        # Adding unique constraint on 'DI', fields ['offset', 'ied']
        db.create_unique('mara_di', ['offset', 'ied_id'])

        # Adding model 'Energy'
        db.create_table('mara_energy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Unit'])),
            ('Ke', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('divider', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_tv', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_ti', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_33_13', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('q', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['Energy'])

        # Adding model 'Event'
        db.create_table('mara_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('di', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.DI'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('subsecond', self.gf('django.db.models.fields.FloatField')()),
            ('q', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['Event'])

        # Adding model 'SV'
        db.create_table('mara_sv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Unit'])),
            ('value', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('mara', ['SV'])

        # Adding unique constraint on 'SV', fields ['offset', 'ied']
        db.create_unique('mara_sv', ['offset', 'ied_id'])

        # Adding model 'AI'
        db.create_table('mara_ai', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Unit'])),
            ('multip_asm', self.gf('django.db.models.fields.FloatField')(default=1.09)),
            ('divider', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_tv', self.gf('django.db.models.fields.FloatField')(default=1, db_column='reltv')),
            ('rel_ti', self.gf('django.db.models.fields.FloatField')(default=1, db_column='relti')),
            ('rel_33_13', self.gf('django.db.models.fields.FloatField')(default=1, db_column='rel33-13')),
            ('q', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='calif')),
        ))
        db.send_create_signal('mara', ['AI'])

        # Adding unique constraint on 'AI', fields ['offset', 'ied']
        db.create_unique('mara_ai', ['offset', 'ied_id'])

        # Adding model 'Unit'
        db.create_table('mara_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('mara', ['Unit'])


    def backwards(self, orm):
        # Removing unique constraint on 'AI', fields ['offset', 'ied']
        db.delete_unique('mara_ai', ['offset', 'ied_id'])

        # Removing unique constraint on 'SV', fields ['offset', 'ied']
        db.delete_unique('mara_sv', ['offset', 'ied_id'])

        # Removing unique constraint on 'DI', fields ['offset', 'ied']
        db.delete_unique('mara_di', ['offset', 'ied_id'])

        # Deleting model 'DI'
        db.delete_table('mara_di')

        # Deleting model 'Energy'
        db.delete_table('mara_energy')

        # Deleting model 'Event'
        db.delete_table('mara_event')

        # Deleting model 'SV'
        db.delete_table('mara_sv')

        # Deleting model 'AI'
        db.delete_table('mara_ai')

        # Deleting model 'Unit'
        db.delete_table('mara_unit')


    models = {
        'mara.ai': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'AI'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'divider': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'multip_asm': ('django.db.models.fields.FloatField', [], {'default': '1.09'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'q': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'calif'"}),
            'rel_33_13': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'rel33-13'"}),
            'rel_ti': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'relti'"}),
            'rel_tv': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'reltv'"}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"})
        },
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
        'mara.di': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'DI'},
            'bit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'q': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.energy': {
            'Ke': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'Meta': {'object_name': 'Energy'},
            'address': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'channel': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'divider': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'rel_33_13': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'rel_ti': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'rel_tv': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.event': {
            'Meta': {'object_name': 'Event'},
            'di': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.DI']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'subsecond': ('django.db.models.fields.FloatField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.ied': {
            'Meta': {'object_name': 'IED'},
            'co_master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.COMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_address': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'mara.profile': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Profile'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1'})
        },
        'mara.sv': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'SV'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'mara.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['mara']