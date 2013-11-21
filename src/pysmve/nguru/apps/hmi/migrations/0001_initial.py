# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SVGScreen'
        db.create_table('hmi_svgscreen', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['hmi.SVGScreen'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='screens', to=orm['mara.Profile'])),
            ('svg', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('hmi', ['SVGScreen'])

        # Adding unique constraint on 'SVGScreen', fields ['prefix', 'profile']
        db.create_unique('hmi_svgscreen', ['prefix', 'profile_id'])

        # Adding model 'Color'
        db.create_table('hmi_color', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Profile'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('color', self.gf('colorful.fields.RGBColorField')(max_length=7)),
        ))
        db.send_create_signal('hmi', ['Color'])

        # Adding model 'SVGPropertyChangeSet'
        db.create_table('color', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mara.Profile'])),
            ('index', self.gf('django.db.models.fields.IntegerField')()),
            ('color', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='colors', null=True, to=orm['hmi.Color'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('hmi', ['SVGPropertyChangeSet'])

        # Adding model 'SVGElement'
        db.create_table('hmi_svgelement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('screen', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='elements', null=True, to=orm['hmi.SVGScreen'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('text', self.gf('django.db.models.fields.CharField')(default='0', max_length=120)),
            ('fill', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('stroke', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mark', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('hmi', ['SVGElement'])

        # Adding model 'Formula'
        db.create_table('hmi_formula', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hmi.SVGElement'], null=True, blank=True)),
            ('attribute', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('formula', self.gf('django.db.models.fields.TextField')()),
            ('last_error', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hmi', ['Formula'])


    def backwards(self, orm):
        # Removing unique constraint on 'SVGScreen', fields ['prefix', 'profile']
        db.delete_unique('hmi_svgscreen', ['prefix', 'profile_id'])

        # Deleting model 'SVGScreen'
        db.delete_table('hmi_svgscreen')

        # Deleting model 'Color'
        db.delete_table('hmi_color')

        # Deleting model 'SVGPropertyChangeSet'
        db.delete_table('color')

        # Deleting model 'SVGElement'
        db.delete_table('hmi_svgelement')

        # Deleting model 'Formula'
        db.delete_table('hmi_formula')


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