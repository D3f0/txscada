# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'EmailNotificationAssociation.cc'
        db.add_column('notifications_emailnotificationassociation', 'cc',
                      self.gf('apps.notifications.fields.CommaSeparatedEmailField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'EmailNotificationAssociation.bcc'
        db.add_column('notifications_emailnotificationassociation', 'bcc',
                      self.gf('apps.notifications.fields.CommaSeparatedEmailField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'EmailNotificationAssociation.cc'
        db.delete_column('notifications_emailnotificationassociation', 'cc')

        # Deleting field 'EmailNotificationAssociation.bcc'
        db.delete_column('notifications_emailnotificationassociation', 'bcc')


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
        'mailer.message': {
            'Meta': {'object_name': 'Message'},
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
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
        'mara.event': {
            'Meta': {'object_name': 'Event'},
            'di': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['mara.DI']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.IntegerField', [], {}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_ack': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
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
        'notifications.emailnotificationassociation': {
            'Meta': {'object_name': 'EmailNotificationAssociation'},
            'bcc': ('apps.notifications.fields.CommaSeparatedEmailField', [], {'null': 'True', 'blank': 'True'}),
            'cc': ('apps.notifications.fields.CommaSeparatedEmailField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'source_di': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'email_associations'", 'symmetrical': 'False', 'to': "orm['mara.DI']"}),
            'targets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'template': ('django.db.models.fields.TextField', [], {'default': "'{{ event }} {{ timestamp }}'"})
        },
        'notifications.messagelogeventrelation': {
            'Meta': {'object_name': 'MessageLogEventRelation'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mara.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mailer.Message']"})
        },
        'notifications.notificationrequest': {
            'Meta': {'object_name': 'NotificationRequest'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_status_change_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'c'", 'max_length': '2'})
        },
        'notifications.smsnotificationassociation': {
            'Meta': {'object_name': 'SMSNotificationAssociation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'source_di': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sms_associations'", 'symmetrical': 'False', 'to': "orm['mara.DI']"}),
            'targets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'template': ('django.db.models.fields.TextField', [], {'default': "'{{ event }} {{ timestamp }}'"})
        }
    }

    complete_apps = ['notifications']