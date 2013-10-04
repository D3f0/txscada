# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'SVGPropertyChangeSet.stroke'
        db.delete_column('color', 'stroke_id')

        # Deleting field 'SVGPropertyChangeSet.fill'
        db.delete_column('color', 'fill_id')

        # Adding field 'SVGPropertyChangeSet.color'
        db.add_column('color', 'color',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='colors', null=True, to=orm['hmi.Color']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'SVGPropertyChangeSet.stroke'
        db.add_column('color', 'stroke',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='strokes', null=True, to=orm['hmi.Color'], blank=True),
                      keep_default=False)

        # Adding field 'SVGPropertyChangeSet.fill'
        db.add_column('color', 'fill',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='fills', null=True, to=orm['hmi.Color'], blank=True),
                      keep_default=False)

        # Deleting field 'SVGPropertyChangeSet.color'
        db.delete_column('color', 'color_id')


    models = {
        'hmi.color': {
            'Meta': {'object_name': 'Color'},
            'color': ('colorful.fields.RGBColorField', [], {'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"})
        },
        'hmi.formula': {
            'Meta': {'object_name': 'Formula'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'formula': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_error': ('django.db.models.fields.TextField', [], {}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmi.SVGElement']", 'null': 'True', 'blank': 'True'})
        },
        'hmi.svgelement': {
            'Meta': {'object_name': 'SVGElement'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fill': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'screen': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'elements'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'stroke': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '120'})
        },
        'hmi.svgpropertychangeset': {
            'Meta': {'ordering': "('-index',)", 'object_name': 'SVGPropertyChangeSet', 'db_table': "'color'"},
            'color': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'colors'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"})
        },
        'hmi.svgscreen': {
            'Meta': {'unique_together': "(('prefix', 'profile'),)", 'object_name': 'SVGScreen'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'screens'", 'to': "orm['mara.Profile']"}),
            'root': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'svg': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'mara.profile': {
            'Meta': {'unique_together': "(('name', 'version'),)", 'object_name': 'Profile'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        }
    }

    complete_apps = ['hmi']