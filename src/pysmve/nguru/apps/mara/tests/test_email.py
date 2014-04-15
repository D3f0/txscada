from django.test import TestCase
from factories import SMVETreeCOMaseterFactory, UserFactory
from datetime import datetime
from mailer.models import Message

class TestEventEmail(TestCase):
    def setUp(self):
        self.co_master = SMVETreeCOMaseterFactory()
        from constance import config
        self.user_0 = UserFactory(username='user0', email='user0@domain.com')
        self.user_1 = UserFactory(username='user1', email='user1@domain.com')
        self.user_2 = UserFactory(username='user2', email='user2@domain.com')
        self.user_3 = UserFactory(username='user3', email='user3@domain.com')
        config.EVENT_0_EMAIL = 'user0,user1'
        config.EVENT_3_EMAIL = 'user2,user3'
        self.timestamp = datetime(2013,12,31,0,0,0, 50000)

    def test_event_type_0(self):
        di = self.co_master.dis[0]
        di.events.create(timestamp=self.timestamp, value=0, q=0)
        self.assertEqual(Message.objects.count(), 2)


    def test_event_type_3(self):
        ied = self.co_master.ieds.all()[0]
        ied.comevent_set.create(motiv=1, timestamp=self.timestamp)
        self.assertEqual(Message.objects.count(), 2)
        assert False