from django.test import Client

from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase, TestApiClient
from apps.mara.tests.factories import SMVETreeCOMaseterFactory, UserFactory
from datetime import datetime


def show_response(response):
    '''Shows response on web browser'''
    import subprocess, tempfile, os
    temp_file_name = tempfile.mktemp(suffix='html')
    with open(temp_file_name, 'w') as fp:
        fp.write(response.content)
    subprocess.call(['firefox', temp_file_name])
    os.unlink(temp_file_name)

# TODO: Move into utils
def logged_client(testcase,
                  permissions=None, groups=None,
                  is_superuser=False):
    '''
    Creates a user, assigns it as user property of testcase
    and logs him into a Django test client which is returned
    '''
    user = 'user%d' % User.objects.count() + 1
    testcase.user = UserFactory(user=user, password=user)
    client = Client()

    return client


class UnauthenitcatedUserHaveNoAccesToApiTest(TestCase):
    def setUp(self):
        pass


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

    # def test_get_list_unauthorzied(self):
    #     '''Access without login should not be allowed'''
    #     self.assertHttpUnauthorized(self.api_client.get(self.list_url,
    #                                 format='json'))

    def test_get_detail_json(self):

        resp = self.api_client.get(self.list_url,
                                   format='json')
        self.assertValidJSONResponse(resp)


