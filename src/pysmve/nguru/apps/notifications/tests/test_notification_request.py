# -*- coding: utf-8 -*-
from django.test import TestCase
from datetime import datetime
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from apps.notifications.utils import SMSServerToolsModem, get_available_modem
import tempfile
import shutil
from unittest import skip
import os
import mock


from apps.mara.tests.factories import (
    SMVETreeCOMaseterFactory,
    EventDescriptionFactory,

    UserFactory
)

from ..models import (
    NotificationRequest,
)

from .factories import (
    SMSNotificationAssociationFactory,
    EmailNotificationAssociationFactory
)
from mailer.models import Message


class TestNotificationRequestsCreation(TestCase):
    def setUp(self):
        self.co_master = SMVETreeCOMaseterFactory()
        self.di = self.co_master.dis[0]
        self.di.tag = 'E0AABBCC'
        self.di.description = 'Equipo de prueba'

        # Texto del evento
        self.timestamp = datetime(2014, 1, 1, 1, 1, 1)
        self.value0 = 0
        EventDescriptionFactory(
            profile=self.co_master.profile,
            textoev2=self.di.idtextoev2,
            value=self.value0,
            text="DESCONECTADO",
        )

        self.user = UserFactory(username='user')
        profile = self.user.get_profile()
        profile.cellphone = '+12345678'
        profile.save()

        self.assoc = SMSNotificationAssociationFactory()
        self.assoc.targets.add(self.user)
        self.assoc.source_di.add(self.di)

    def test_events_are_created(self):
        # Crear un evento
        NotificationRequest.objects.all().delete()

        self.di.events.create(
            timestamp=self.timestamp,
            q=0,
            value=1,
        )
        self.assertEqual(NotificationRequest.objects.count(), 1)


class TestNotificationMessageCreation(TestCase):

    def setUp(self):
        self.co_master = SMVETreeCOMaseterFactory()
        self.di = self.co_master.dis[0]
        self.di.tag = 'E0AABBCC'
        self.di.description = 'Equipo de prueba'

        # Texto del evento
        self.timestamp = datetime(2014, 1, 1, 1, 1, 1)
        self.value0 = 0
        EventDescriptionFactory(
            profile=self.co_master.profile,
            textoev2=self.di.idtextoev2,
            value=self.value0,
            text="DESCONECTADO",
        )

        self.user = UserFactory(username='user', email='gaga@gaga.com')

        self.assoc = EmailNotificationAssociationFactory()
        self.assoc.targets.add(self.user)
        self.assoc.source_di.add(self.di)

    def test_events_are_created(self):
        # Crear un evento
        NotificationRequest.objects.all().delete()

        event = self.di.events.create(
            timestamp=self.timestamp,
            q=0,
            value=1,
        )
        self.assertEqual(Message.objects.count(), 1)

        message = Message.objects.get()

        pk = message.related_events.get().pk

        self.assertEqual(event.pk, pk)


FIXED_DATE = datetime(2014, 1, 1, 23, 59, 59)


class TestNotificationFilesCreatedForSMSServerToolsModem(TestCase):
    def setUp(self):
        self.path = tempfile.mkdtemp('smve-outoging-sms')
        self.modem = SMSServerToolsModem(outoging_queue=self.path)
        self.modem.get_current_time_formated = mock.MagicMock()
        self.fixed_date = '20120101235959'
        self.modem.get_current_time_formated.return_value = self.fixed_date

    def test_sms_created_for_sms_server_tools_without_id(self):

        to = 5492804123456
        message = 'Esta es una prueba'
        self.modem.send_sms(to, message)
        expedted_file_path = os.path.join(
            self.path, self.fixed_date + '-' + str(to) + '-' + 'NA'
        )
        assert os.path.exists(expedted_file_path)
        with open(expedted_file_path) as fp:
            data = fp.read()
        import pdb; pdb.set_trace()
        os.unlink(expedted_file_path)

    def test_sms_created_for_sms_server_tools_with_id(self):

        to = 5492804123456
        msg_id = 1234
        message = 'Esta es una prueba'
        self.modem.send_sms(to, message, msg_id)
        expedted_file_path = os.path.join(
            self.path, self.fixed_date + '-' + str(to) + '-' + str(msg_id)
        )
        assert os.path.exists(expedted_file_path)
        os.unlink(expedted_file_path)

    def tearDown(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def test_create_message_file(self):
        NotificationRequest.objects.all().delete()
        with self.settings():
            pass


class ModemA(object):
    """Dummy class"""
    pass


class ModemB(object):
    """Dummy class"""
    pass


class TestModemConfiguration(TestCase):
    def setUp(self):
        pass

    def test_configuration(self):

        with self.settings(SMS_MODEM_CLASS='nguru.apps.notifications.tests.'
                           'test_notification_request.ModemA'):
            available_modem = get_available_modem()
            self.assertIsInstance(available_modem, ModemA)
        with self.settings(SMS_MODEM_CLASS='nguru.apps.notifications.tests.'
                           'test_notification_request.ModemB'):
            available_modem = get_available_modem()
            self.assertIsInstance(available_modem, ModemB)


@skip(u"Falta evaluar que falla con WebTest")
class TestUserProfileShowsInternationalNumbers(WebTest):
    def setUp(self):
        self.user = UserFactory(username="admin", is_superuser=True, is_staff=True)
        self.user1 = UserFactory(username="someone")
        self.url = reverse('admin:auth_user_change', args=(self.user1.pk, ))

    def test_phonenumber_is_validated(self):
        from apps.hmi.models import UserProfile
        response = self.app.get(self.url, user=self.user)
        response.form.fields['userprofile_set-0-cellphone'] = '123'
        response.showbrowser()

        response = response.form.submit('_save').follow()
        profile = self.user1.get_profile()
        assert False
