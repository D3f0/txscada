# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ComEvent'
        db.create_table('eventcom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.ComEventKind'])),
            ('motiv', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['ComEvent'])

        # Adding model 'ComEventKind'
        db.create_table('com', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('texto_2', self.gf('django.db.models.fields.IntegerField')()),
            ('pesoaccion', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['ComEventKind'])

        # Adding model 'EventKind'
        db.create_table('mara_eventkind', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('trigger_up', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('trigger_down', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('mara', ['EventKind'])

        # Adding field 'Event.kind'
        db.add_column('mara_event', 'kind',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.EventKind'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ComEvent'
        db.delete_table('eventcom')

        # Deleting model 'ComEventKind'
        db.delete_table('com')

        # Deleting model 'EventKind'
        db.delete_table('mara_eventkind')

        # Deleting field 'Event.kind'
        db.delete_column('mara_event', 'kind_id')


    models = {
        'mara.ai': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'AI'},
            'c_factor': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'multip_asm': ('django.db.models.fields.FloatField', [], {'default': '1.09'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'calif'"}),
            'rel_33_13': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'rel33-13'"}),
            'rel_ti': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'relti'"}),
            'rel_tv': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'reltv'"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'})
        },
        'mara.comaster': {
            'Meta': {'object_name': 'COMaster'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exponential_backoff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'max_retry_before_offline': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'peh_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(1, 0)'}),
            'poll_interval': ('django.db.models.fields.FloatField', [], {'default': '5'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '9761'}),
            'process_pid': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comasters'", 'to': "orm['mara.Profile']"}),
            'rs485_destination': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_source': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.comevent': {
            'Meta': {'object_name': 'ComEvent', 'db_table': "'eventcom'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.ComEventKind']"}),
            'motiv': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.comeventkind': {
            'Meta': {'ordering': "('code',)", 'object_name': 'ComEventKind', 'db_table': "'com'"},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pesoaccion': ('django.db.models.fields.IntegerField', [], {}),
            'texto_2': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.di': {
            'Meta': {'unique_together': "(('offset', 'ied', 'port', 'bit'),)", 'object_name': 'DI'},
            'bit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'q': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.energy': {
            'Meta': {'object_name': 'Energy', 'db_table': "'energy'"},
            'energy_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.EnergyPoint']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.energypoint': {
            'Meta': {'object_name': 'EnergyPoint'},
            'channel': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'divider': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'ke': ('django.db.models.fields.FloatField', [], {'default': '0.025'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'rel_33_13': ('django.db.models.fields.FloatField', [], {'default': '2.5'}),
            'rel_ti': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'rel_tv': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"})
        },
        'mara.event': {
            'Meta': {'object_name': 'Event'},
            'di': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.DI']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.EventKind']", 'null': 'True', 'blank': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_ack': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.eventkind': {
            'Meta': {'object_name': 'EventKind'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'trigger_down': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'trigger_up': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'mara.ied': {
            'Meta': {'ordering': "('offset',)", 'unique_together': "(('co_master', 'rs485_address'),)", 'object_name': 'IED'},
            'co_master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ieds'", 'to': "orm['mara.COMaster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_address': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'mara.profile': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'Profile'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'mara.sv': {
            'Meta': {'ordering': "('ied__offset', 'offset')", 'unique_together': "(('offset', 'ied', 'bit'),)", 'object_name': 'SV'},
            'bit': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['mara']