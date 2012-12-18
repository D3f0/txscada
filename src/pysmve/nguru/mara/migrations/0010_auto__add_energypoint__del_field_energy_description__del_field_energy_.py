# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EnergyPoint'
        db.create_table('mara_energypoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ied', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.IED'])),
            ('offset', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('param', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Unit'])),
            ('ke', self.gf('django.db.models.fields.FloatField')(default=0.025)),
            ('divider', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_tv', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_ti', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('rel_33_13', self.gf('django.db.models.fields.FloatField')(default=2.5)),
        ))
        db.send_create_signal('mara', ['EnergyPoint'])

        # Deleting field 'Energy.description'
        db.delete_column('mara_energy', 'description')

        # Deleting field 'Energy.Ke'
        db.delete_column('mara_energy', 'Ke')

        # Deleting field 'Energy.rel_tv'
        db.delete_column('mara_energy', 'rel_tv')

        # Deleting field 'Energy.rel_ti'
        db.delete_column('mara_energy', 'rel_ti')

        # Deleting field 'Energy.offset'
        db.delete_column('mara_energy', 'offset')

        # Deleting field 'Energy.rel_33_13'
        db.delete_column('mara_energy', 'rel_33_13')

        # Deleting field 'Energy.param'
        db.delete_column('mara_energy', 'param')

        # Deleting field 'Energy.ied'
        db.delete_column('mara_energy', 'ied_id')

        # Deleting field 'Energy.unit'
        db.delete_column('mara_energy', 'unit_id')

        # Deleting field 'Energy.address'
        db.delete_column('mara_energy', 'address')

        # Deleting field 'Energy.divider'
        db.delete_column('mara_energy', 'divider')

        # Deleting field 'Energy.channel'
        db.delete_column('mara_energy', 'channel')

        # Adding field 'Energy.energy_point'
        db.add_column('mara_energy', 'energy_point',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['mara.EnergyPoint']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'EnergyPoint'
        db.delete_table('mara_energypoint')

        # Adding field 'Energy.description'
        db.add_column('mara_energy', 'description',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Energy.Ke'
        db.add_column('mara_energy', 'Ke',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'Energy.rel_tv'
        db.add_column('mara_energy', 'rel_tv',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'Energy.rel_ti'
        db.add_column('mara_energy', 'rel_ti',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'Energy.offset'
        db.add_column('mara_energy', 'offset',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Energy.rel_33_13'
        db.add_column('mara_energy', 'rel_33_13',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'Energy.param'
        db.add_column('mara_energy', 'param',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Energy.ied'
        raise RuntimeError("Cannot reverse this migration. 'Energy.ied' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Energy.unit'
        raise RuntimeError("Cannot reverse this migration. 'Energy.unit' and its values cannot be restored.")
        # Adding field 'Energy.address'
        db.add_column('mara_energy', 'address',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Energy.divider'
        db.add_column('mara_energy', 'divider',
                      self.gf('django.db.models.fields.FloatField')(default=1),
                      keep_default=False)

        # Adding field 'Energy.channel'
        db.add_column('mara_energy', 'channel',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'Energy.energy_point'
        db.delete_column('mara_energy', 'energy_point_id')


    models = {
        'mara.ai': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'AI'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'divider': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'multip_asm': ('django.db.models.fields.FloatField', [], {'default': '1.09'}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
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
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comasters'", 'to': "orm['mara.Profile']"}),
            'rs485_destination': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_source': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.di': {
            'Meta': {'unique_together': "(('offset', 'ied', 'port', 'bit'),)", 'object_name': 'DI'},
            'bit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'q': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mara.energy': {
            'Meta': {'object_name': 'Energy'},
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
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'rel_33_13': ('django.db.models.fields.FloatField', [], {'default': '2.5'}),
            'rel_ti': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'rel_tv': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"})
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
            'Meta': {'unique_together': "(('co_master', 'rs485_address'),)", 'object_name': 'IED'},
            'co_master': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ieds'", 'to': "orm['mara.COMaster']"}),
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Unit']"}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.unit': {
            'Meta': {'object_name': 'Unit'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['mara']