# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SVGPropertyChangeSet'
        db.create_table('color', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('background', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='backgrounds', null=True, to=orm['hmi.Color'])),
            ('foreground', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='foregrounds', null=True, to=orm['hmi.Color'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('hmi', ['SVGPropertyChangeSet'])


    def backwards(self, orm):
        # Deleting model 'SVGPropertyChangeSet'
        db.delete_table('color')


    models = {
        'hmi.color': {
            'Meta': {'object_name': 'Color'},
            'color': ('colorful.fields.RGBColorField', [], {'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
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