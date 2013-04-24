# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'SVGElement.colback'
        db.delete_column('hmi_svgelement', 'colback')

        # Adding field 'SVGElement.background'
        db.add_column('hmi_svgelement', 'background',
                      self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True),
                      keep_default=False)


        # Changing field 'SVGElement.text'
        db.alter_column('hmi_svgelement', 'text', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

    def backwards(self, orm):
        # Adding field 'SVGElement.colback'
        db.add_column('hmi_svgelement', 'colback',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=20),
                      keep_default=False)

        # Deleting field 'SVGElement.background'
        db.delete_column('hmi_svgelement', 'background')


        # Changing field 'SVGElement.text'
        db.alter_column('hmi_svgelement', 'text', self.gf('django.db.models.fields.CharField')(default=None, max_length=20))

    models = {
        'hmi.color': {
            'Meta': {'object_name': 'Color'},
            'color': ('colorful.fields.RGBColorField', [], {'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'hmi.formula': {
            'Meta': {'object_name': 'Formula'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'formula': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'hmi.svgelement': {
            'Meta': {'object_name': 'SVGElement'},
            'background': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'hmi.svgpropertychangeset': {
            'Meta': {'object_name': 'SVGPropertyChangeSet', 'db_table': "'color'"},
            'background': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backgrounds'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'foreground': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'foregrounds'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {})
        },
        'hmi.svgscreen': {
            'Meta': {'object_name': 'SVGScreen'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'root': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'svg': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['hmi']