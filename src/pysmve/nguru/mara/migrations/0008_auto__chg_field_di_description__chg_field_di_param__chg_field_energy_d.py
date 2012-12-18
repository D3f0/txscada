# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'DI.description'
        db.alter_column('mara_di', 'description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'DI.param'
        db.alter_column('mara_di', 'param', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'Energy.description'
        db.alter_column('mara_energy', 'description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Energy.param'
        db.alter_column('mara_energy', 'param', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))
        # Adding field 'SV.width'
        db.add_column('mara_sv', 'width',
                      self.gf('django.db.models.fields.IntegerField')(default=8),
                      keep_default=False)


        # Changing field 'SV.description'
        db.alter_column('mara_sv', 'description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'SV.param'
        db.alter_column('mara_sv', 'param', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'AI.description'
        db.alter_column('mara_ai', 'description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'AI.param'
        db.alter_column('mara_ai', 'param', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'DI.description'
        raise RuntimeError("Cannot reverse this migration. 'DI.description' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'DI.param'
        raise RuntimeError("Cannot reverse this migration. 'DI.param' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Energy.description'
        raise RuntimeError("Cannot reverse this migration. 'Energy.description' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Energy.param'
        raise RuntimeError("Cannot reverse this migration. 'Energy.param' and its values cannot be restored.")
        # Deleting field 'SV.width'
        db.delete_column('mara_sv', 'width')


        # User chose to not deal with backwards NULL issues for 'SV.description'
        raise RuntimeError("Cannot reverse this migration. 'SV.description' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'SV.param'
        raise RuntimeError("Cannot reverse this migration. 'SV.param' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'AI.description'
        raise RuntimeError("Cannot reverse this migration. 'AI.description' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'AI.param'
        raise RuntimeError("Cannot reverse this migration. 'AI.param' and its values cannot be restored.")

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
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'rs485_destination': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'rs485_source': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        'mara.di': {
            'Meta': {'unique_together': "(('offset', 'ied'),)", 'object_name': 'DI'},
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
            'Ke': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'Meta': {'object_name': 'Energy'},
            'address': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'channel': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'divider': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.IED']"}),
            'offset': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'param': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
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
            'Meta': {'unique_together': "(('co_master', 'rs485_address'),)", 'object_name': 'IED'},
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