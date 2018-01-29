# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        SVGElement = orm.models['hmi.svgelement']
        query = models.Q(tag__icontains='89I') | models.Q(tag__icontains='89S')
        for elem in SVGElement.objects.filter(query):
            if '89I' in elem.tag:
                elem.linked_text_change = elem.tag.replace('89I', '89S')
            else:
                elem.linked_text_change = elem.tag.replace('89S', '89I')

            elem.on_click_text_toggle = '1 (Cerrado), 0 (Abierto)'
            elem.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        SVGElement = orm.models['hmi.svgelement']
        query = models.Q(tag__icontains='89I') | models.Q(tag__icontains='89S')
        for elem in SVGElement.objects.filter(query):
            elem.linked_text_change = ''
            elem.on_click_text_toggle = ''
            elem.save()

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
            'last_error': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmi.SVGElement']", 'null': 'True', 'blank': 'True'})
        },
        'hmi.svgelement': {
            'Meta': {'object_name': 'SVGElement'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fill': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'linked_text_change': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'on_click_jump': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hmi.SVGScreen']", 'null': 'True', 'blank': 'True'}),
            'on_click_text_toggle': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'screen': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'elements'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'stroke': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '120', 'blank': 'True'})
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'screens'", 'to': "orm['mara.Profile']"}),
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
    symmetrical = True
