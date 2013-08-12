# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        Profile = orm.models['mara.profile']
        default = Profile.objects.all()[0]
        # Adding field 'Color.profile'
        db.add_column('hmi_color', 'profile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=default.pk, to=orm['mara.Profile']),
                      keep_default=False)

        # Adding field 'Formula.profile'
        db.add_column('hmi_formula', 'profile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=default.pk, to=orm['mara.Profile']),
                      keep_default=False)

        # Adding field 'SVGPropertyChangeSet.profile'
        db.add_column('color', 'profile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=default.pk, to=orm['mara.Profile']),
                      keep_default=False)

        # Adding field 'SVGElement.profile'
        db.add_column('hmi_svgelement', 'profile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=default.pk, to=orm['mara.Profile']),
                      keep_default=False)

        # Adding field 'SVGScreen.profile'
        db.add_column('hmi_svgscreen', 'profile',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=default.pk, to=orm['mara.Profile']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Color.profile'
        db.delete_column('hmi_color', 'profile_id')

        # Deleting field 'Formula.profile'
        db.delete_column('hmi_formula', 'profile_id')

        # Deleting field 'SVGPropertyChangeSet.profile'
        db.delete_column('color', 'profile_id')

        # Deleting field 'SVGElement.profile'
        db.delete_column('hmi_svgelement', 'profile_id')

        # Deleting field 'SVGScreen.profile'
        db.delete_column('hmi_svgscreen', 'profile_id')


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
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'hmi.svgelement': {
            'Meta': {'object_name': 'SVGElement'},
            'background': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'hmi.svgpropertychangeset': {
            'Meta': {'object_name': 'SVGPropertyChangeSet', 'db_table': "'color'"},
            'background': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'backgrounds'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'foreground': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'foregrounds'", 'null': 'True', 'to': "orm['hmi.Color']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"})
        },
        'hmi.svgscreen': {
            'Meta': {'object_name': 'SVGScreen'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['hmi.SVGScreen']"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Profile']"}),
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