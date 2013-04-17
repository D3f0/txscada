# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'EnergyPoint'
        db.delete_table('mara_energypoint')

        # Deleting model 'EventKind'
        db.delete_table('mara_eventkind')

        # Deleting field 'Energy.energy_point'
        db.delete_column('mara_energy', 'energy_point_id')

        # Adding field 'Energy.hnn'
        db.add_column('mara_energy', 'hnn',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Energy.ai'
        db.add_column('mara_energy', 'ai',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['mara.AI']),
                      keep_default=False)

        # Adding field 'Energy.code'
        db.add_column('mara_energy', 'code',
                      self.gf('django.db.models.fields.IntegerField')(default=None),
                      keep_default=False)

        # Deleting field 'Event.kind'
        db.delete_column('mara_event', 'kind_id')


    def backwards(self, orm):
        # Adding model 'EnergyPoint'
        db.create_table('mara_energypoint', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('ke', self.gf('django.db.models.fields.FloatField')(default=0.025)),
            ('rel_tv', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_ti', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('trasducer', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('rel_33_13', self.gf('django.db.models.fields.FloatField')(default=2.5)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Unit'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('divider', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mara', ['EnergyPoint'])

        # Adding model 'EventKind'
        db.create_table('mara_eventkind', (
            ('trigger_down', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trigger_up', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('mara', ['EventKind'])

        # Adding field 'Energy.energy_point'
        db.add_column('energy', 'energy_point',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['mara.EnergyPoint']),
                      keep_default=False)

        # Deleting field 'Energy.hnn'
        db.delete_column('mara_energy', 'hnn')

        # Deleting field 'Energy.ai'
        db.delete_column('mara_energy', 'ai_id')

        # Deleting field 'Energy.code'
        db.delete_column('mara_energy', 'code')

        # Adding field 'Event.kind'
        db.add_column('mara_event', 'kind',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.EventKind'], null=True, blank=True),
                      keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mara.ai': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'AI'},
            'channel': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'delta_h': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'delta_l': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'divider': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'escala': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idtextoevm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'multip_asm': ('django.db.models.fields.FloatField', [], {'default': '1.09'}),
            'noroai': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'pesoaccion_h': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pesoaccion_l': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'q'"}),
            'rel_33_13': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'rel33-13'"}),
            'rel_ti': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'relti'"}),
            'rel_tv': ('django.db.models.fields.FloatField', [], {'default': '1', 'db_column': "'reltv'"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'trasducer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'value_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'motiv': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_ack': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
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
            'trasducer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.energy': {
            'Meta': {'object_name': 'Energy'},
            'ai': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.AI']"}),
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'hnn': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.event': {
            'Meta': {'object_name': 'Event'},
            'di': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.DI']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_ack': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
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
            'trasducer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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