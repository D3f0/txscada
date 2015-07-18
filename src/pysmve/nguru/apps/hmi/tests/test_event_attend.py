from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase, TestApiClient
from apps.mara.tests.factories import SMVETreeCOMaseterFactory, UserFactory
from datetime import datetime
from django_webtest import WebTest
import unittest


class UnauthenitcatedUserHaveNoAccesToApiTest(WebTest, unittest.TestCase):
    def setUp(self):
        self.url = reverse('api_v1_top_level', kwargs={'api_name': 'v1'})

    def test_endpoints_are_protected(self):
        response = self.app.get(self.url)
        # Every endpoint of the exposed API should be protected
        for resource, data in response.json.iteritems():
            url = data['list_endpoint']
            with self.assertRaises(Exception):
                response = self.app.get(url)


class AttendEventsTest(ResourceTestCase):

    def setUp(self):
        self.api_client = TestApiClient()
        self.username = 'user1'
        self.password = 'user1'
        self.user = UserFactory(username=self.username,
                                password=self.password)

        self.get_credentials()

        # Setup Mara
        self.co_master = SMVETreeCOMaseterFactory()
        timestamp = datetime(2014, 1, 1, 12, 30, 0)
        self.event = self.co_master.dis[0].events.create(timestamp=timestamp,
                                                         q=0,
                                                         value=0
                                                         )
        self.detail_url = reverse('api_dispatch_detail', kwargs={
                                  'pk': self.event.pk,
                                  'resource_name': 'event',
                                  'api_name': 'v1'
                                  })

        self.list_url = reverse('api_dispatch_list', kwargs={'api_name': 'v1',
                                'resource_name': 'event'})

    def get_credentials(self):
        result = self.api_client.client.login(username=self.username,
                                              password=self.password)
        return result
