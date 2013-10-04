# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'SVGPropertyChangeSet.foreground'
        db.delete_column('color', 'foreground_id')

        # Deleting field 'SVGPropertyChangeSet.background'
        db.delete_column('color', 'background_id')

        # Adding field 'SVGPropertyChangeSet.fill_back'
        db.add_column('color', 'fill_back',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='backgrounds', null=True, to=orm['hmi.Color']),
                      keep_default=False)

        # Adding field 'SVGPropertyChangeSet.fill_fore'
        db.add_column('color', 'fill_fore',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='foregrounds', null=True, to=orm['hmi.Color']),
                      keep_default=False)

        # Adding field 'SVGPropertyChangeSet.stroke'
        db.add_column('color', 'stroke',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='strokes', null=True, to=orm['hmi.Color']),
                      keep_default=False)

        # Deleting field 'SVGElement.colbak'
        db.delete_column('hmi_svgelement', 'colbak')

        # Adding field 'SVGElement.fill_back'
        db.add_column('hmi_svgelement', 'fill_back',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'SVGElement.fill_fore'
        db.add_column('hmi_svgelement', 'fill_fore',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'SVGElement.stroke'
        db.add_column('hmi_svgelement', 'stroke',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'SVGPropertyChangeSet.foreground'
        db.add_column('color', 'foreground',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='foregrounds', null=True, to=orm['hmi.Color'], blank=True),
                      keep_default=False)

        # Adding field 'SVGPropertyChangeSet.background'
        db.add_column('color', 'background',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='backgrounds', null=True, to=orm['hmi.Color'], blank=True),
                      keep_default=False)

        # Deleting field 'SVGPropertyChangeSet.fill_back'
        db.delete_column('color', 'fill_back_id')

        # Deleting field 'SVGPropertyChangeSet.fill_fore'
        db.delete_column('color', 'fill_fore_id')

        # Deleting field 'SVGPropertyChangeSet.stroke'
        db.delete_column('color', 'stroke_id')

        # Adding field 'SVGElement.colbak'
        db.add_column('hmi_svgelement', 'colbak',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'SVGElement.fill_back'
        db.delete_column('hmi_svgelement', 'fill_back')

        # Deleting field 'SVGElement.fill_fore'
        db.delete_column('hmi_svgelement', 'fill_fore')

        # Deleting field 'SVGElement.stroke'
        db.delete_column('hmi_svgelement', 'stroke')


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
            'fill_back': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fill_fore': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'screen': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'elements'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'stroke': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '120'})
        },
        'hmi.svgpropertychangeset': {
            'Meta': {'ordering': "('-index',)", 'object_name': 'SVGPropertyChangeSet', 'db_table': "'color'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'fill_back': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backgrounds'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'fill_fore': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'foregrounds'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'stroke': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'strokes'", 'null': 'True', 'to': "orm['hmi.Color']"})
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