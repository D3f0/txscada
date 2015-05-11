# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NotificationAssociation'
        db.create_table('notifications_notificationassociation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('notifications', ['NotificationAssociation'])

        # Adding M2M table for field source_di on 'NotificationAssociation'
        m2m_table_name = db.shorten_name('notifications_notificationassociation_source_di')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notificationassociation', models.ForeignKey(orm['notifications.notificationassociation'], null=False)),
            ('di', models.ForeignKey(orm['mara.di'], null=False))
        ))
        db.create_unique(m2m_table_name, ['notificationassociation_id', 'di_id'])

        # Adding M2M table for field targets on 'NotificationAssociation'
        m2m_table_name = db.shorten_name('notifications_notificationassociation_targets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notificationassociation', models.ForeignKey(orm['notifications.notificationassociation'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['notificationassociation_id', 'user_id'])

        # Adding model 'NotificationRequest'
        db.create_table('notifications_notificationrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('last_status_change_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='c', max_length=2)),
            ('error', self.gf('django.db.models.fields.TextField')()),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('notifications', ['NotificationRequest'])


    def backwards(self, orm):
        # Deleting model 'NotificationAssociation'
        db.delete_table('notifications_notificationassociation')

        # Removing M2M table for field source_di on 'NotificationAssociation'
        db.delete_table(db.shorten_name('notifications_notificationassociation_source_di'))

        # Removing M2M table for field targets on 'NotificationAssociation'
        db.delete_table(db.shorten_name('notifications_notificationassociation_targets'))

        # Deleting model 'NotificationRequest'
        db.delete_table('notifications_notificationrequest')


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
        'mara.comaster': {
            'Meta': {'object_name': 'COMaster'},
            'custom_payload': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'custom_payload_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exponential_backoff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_peh': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'max_retry_before_offline': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'peh_time': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0, 3600)'}),
            'poll_interval': ('django.db.models.fields.FloatField', [], {'default': '5'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '9761'}),
            'process_pid': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comasters'", 'to': "orm['mara.Profile']"}),
            'rs485_destination': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'rs485_source': ('django.db.models.fields.SmallIntegerField', [], {'default': '64'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'tipo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trasducer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
        'notifications.notificationassociation': {
            'Meta': {'object_name': 'NotificationAssociation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source_di': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mara.DI']", 'symmetrical': 'False'}),
            'targets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'notifications.notificationrequest': {
            'Meta': {'object_name': 'NotificationRequest'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'error': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_status_change_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'c'", 'max_length': '2'})
        }
    }

    complete_apps = ['notifications']