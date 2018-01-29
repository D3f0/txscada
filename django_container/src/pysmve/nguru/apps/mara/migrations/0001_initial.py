# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table('mara_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mara', ['Profile'])

        # Adding unique constraint on 'Profile', fields ['name', 'version']
        db.create_unique('mara_profile', ['name', 'version'])

        # Adding model 'COMaster'
        db.create_table('mara_comaster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comasters', to=orm['mara.Profile'])),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=9761)),
            ('poll_interval', self.gf('django.db.models.fields.FloatField')(default=5)),
            ('exponential_backoff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('max_retry_before_offline', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('sequence', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rs485_source', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('rs485_destination', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('process_pid', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('peh_time', self.gf('django.db.models.fields.TimeField')(default=datetime.time(1, 0))),
        ))
        db.send_create_signal('mara', ['COMaster'])

        # Adding model 'IED'
        db.create_table('mara_ied', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('co_master', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ieds', to=orm['mara.COMaster'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('rs485_address', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('mara', ['IED'])

        # Adding unique constraint on 'IED', fields ['co_master', 'rs485_address']
        db.create_unique('mara_ied', ['co_master_id', 'rs485_address'])

        # Adding model 'SV'
        db.create_table('mara_sv', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('trasducer', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('bit', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mara', ['SV'])

        # Adding unique constraint on 'SV', fields ['offset', 'ied', 'bit']
        db.create_unique('mara_sv', ['offset', 'ied_id', 'bit'])

        # Adding model 'DI'
        db.create_table('mara_di', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('trasducer', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('q', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maskinv', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('nrodi', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('idtextoev2', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('pesoaccion_h', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('pesoaccion_l', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mara', ['DI'])

        # Adding unique constraint on 'DI', fields ['offset', 'ied', 'port', 'bit']
        db.create_unique('mara_di', ['offset', 'ied_id', 'port', 'bit'])

        # Adding model 'Event'
        db.create_table('mara_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('di', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['mara.DI'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('timestamp_ack', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('q', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['Event'])

        # Adding model 'EventText'
        db.create_table('mara_eventtext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_kinds', to=orm['mara.Profile'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('idtextoev2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pesoaccion', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('mara', ['EventText'])

        # Adding unique constraint on 'EventText', fields ['idtextoev2', 'value']
        db.create_unique('mara_eventtext', ['idtextoev2', 'value'])

        # Adding model 'EventDescription'
        db.create_table('mara_eventdescription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Profile'])),
            ('textoev2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('mara', ['EventDescription'])

        # Adding model 'ComEventKind'
        db.create_table('com', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('texto_2', self.gf('django.db.models.fields.IntegerField')()),
            ('pesoaccion', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['ComEventKind'])

        # Adding model 'ComEvent'
        db.create_table('eventcom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('timestamp_ack', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('motiv', self.gf('django.db.models.fields.IntegerField')()),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.ComEventKind'], null=True, blank=True)),
        ))
        db.send_create_signal('mara', ['ComEvent'])

        # Adding model 'AI'
        db.create_table('mara_ai', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('trasducer', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('multip_asm', self.gf('django.db.models.fields.FloatField')(default=1.09)),
            ('divider', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_tv', self.gf('django.db.models.fields.FloatField')(default=1, db_column='reltv')),
            ('rel_ti', self.gf('django.db.models.fields.FloatField')(default=1, db_column='relti')),
            ('rel_33_13', self.gf('django.db.models.fields.FloatField')(default=1, db_column='rel33-13')),
            ('q', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='q')),
            ('value', self.gf('django.db.models.fields.SmallIntegerField')(default=-1)),
            ('escala', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('nroai', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('idtextoevm', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('value_max', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('value_min', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('delta_h', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('delta_l', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('idtextoev2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pesoaccion_h', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pesoaccion_l', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('mara', ['AI'])

        # Adding unique constraint on 'AI', fields ['offset', 'ied']
        db.create_unique('mara_ai', ['offset', 'ied_id'])

        # Adding model 'Energy'
        db.create_table('mara_energy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ai', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.AI'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('hnn', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('q', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('mara', ['Energy'])

        # Adding model 'Action'
        db.create_table('mara_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Profile'])),
            ('bit', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('script', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('arguments', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('mara', ['Action'])

        # Adding unique constraint on 'Action', fields ['bit']
        db.create_unique('mara_action', ['bit'])


    def backwards(self, orm):
        # Removing unique constraint on 'Action', fields ['bit']
        db.delete_unique('mara_action', ['bit'])

        # Removing unique constraint on 'AI', fields ['offset', 'ied']
        db.delete_unique('mara_ai', ['offset', 'ied_id'])

        # Removing unique constraint on 'EventText', fields ['idtextoev2', 'value']
        db.delete_unique('mara_eventtext', ['idtextoev2', 'value'])

        # Removing unique constraint on 'DI', fields ['offset', 'ied', 'port', 'bit']
        db.delete_unique('mara_di', ['offset', 'ied_id', 'port', 'bit'])

        # Removing unique constraint on 'SV', fields ['offset', 'ied', 'bit']
        db.delete_unique('mara_sv', ['offset', 'ied_id', 'bit'])

        # Removing unique constraint on 'IED', fields ['co_master', 'rs485_address']
        db.delete_unique('mara_ied', ['co_master_id', 'rs485_address'])

        # Removing unique constraint on 'Profile', fields ['name', 'version']
        db.delete_unique('mara_profile', ['name', 'version'])

        # Deleting model 'Profile'
        db.delete_table('mara_profile')

        # Deleting model 'COMaster'
        db.delete_table('mara_comaster')

        # Deleting model 'IED'
        db.delete_table('mara_ied')

        # Deleting model 'SV'
        db.delete_table('mara_sv')

        # Deleting model 'DI'
        db.delete_table('mara_di')

        # Deleting model 'Event'
        db.delete_table('mara_event')

        # Deleting model 'EventText'
        db.delete_table('mara_eventtext')

        # Deleting model 'EventDescription'
        db.delete_table('mara_eventdescription')

        # Deleting model 'ComEventKind'
        db.delete_table('com')

        # Deleting model 'ComEvent'
        db.delete_table('eventcom')

        # Deleting model 'AI'
        db.delete_table('mara_ai')

        # Deleting model 'Energy'
        db.delete_table('mara_energy')

        # Deleting model 'Action'
        db.delete_table('mara_action')


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
        'mara.action': {
            'Meta': {'unique_together': "(('bit',),)", 'object_name': 'Action'},
            'arguments': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'bit': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'script': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'idtextoev2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'idtextoevm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'multip_asm': ('django.db.models.fields.FloatField', [], {'default': '1.09'}),
            'nroai': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.ComEventKind']", 'null': 'True', 'blank': 'True'}),
            'motiv': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_ack': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'mara.comeventkind': {
            'Meta': {'ordering': "('code',)", 'object_name': 'ComEventKind', 'db_table': "'com'"},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pesoaccion': ('django.db.models.fields.IntegerField', [], {}),
            'texto_2': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.di': {
            'Meta': {'ordering': "('port', 'bit')", 'unique_together': "(('offset', 'ied', 'port', 'bit'),)", 'object_name': 'DI'},
            'bit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idtextoev2': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'maskinv': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nrodi': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'pesoaccion_h': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pesoaccion_l': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
            'di': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['mara.DI']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_ack': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.eventdescription': {
            'Meta': {'object_name': 'EventDescription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'textoev2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'mara.eventtext': {
            'Meta': {'unique_together': "(('idtextoev2', 'value'),)", 'object_name': 'EventText'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idtextoev2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pesoaccion': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_kinds'", 'to': "orm['mara.Profile']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'param': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'trasducer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['mara']