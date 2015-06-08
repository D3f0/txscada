from django.test import TestCase
from datetime import datetime

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


