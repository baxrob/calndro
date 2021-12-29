import json
from pathlib import Path
import ipdb

from schedul.models import Event, TimeSpan
from schedul.serializers import EventSerializer, TimeSpanSerializer

from rest_framework.test import (
    APIRequestFactory, APITestCase, 
    APILiveServerTestCase, URLPatternsTestCase,
    force_authenticate,
    RequestsClient
)

# x csrf, auth x env, logging
# email, m/t q

class EventTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        bpath = Path(__file__).resolve().parent / 'fixtures'
        fdata = {}
        for f in cls.fixtures:
            fpath = bpath / (f + '.json')
            with open(fpath) as fd:
                fdata[f] = json.loads(fd.read())
        cls.fdata = {
            'spans': ([(x['fields']['begin'], x['fields']['duration']) 
                for x in fdata['schedul'] 
                if x['model'] == 'schedul.timespan']),
            'emails': [x['fields']['email'] for x in fdata['users']],
            'users': [x['pk'] for x in fdata['users']],
            'events': ([x['pk'] for x in fdata['schedul']
                if x['model'] == 'schedul.event'])
        }
        ipdb.set_trace()

    def setUp(self):
        print(self.fixtures)
        print(self.fdata)
        assert(True)

    def get_spans(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['spans'][n:n+m]]

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]


    #
    def test_get_list(self):
        response = self.client.get('/')
        print(response.content)
        assert(response.status_code == 200)
        ipdb.set_trace()

    def test_post_single(self):
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'span': self.get_spans(0, len(self.fdata['spans']))
        })#, format='json')
        ipdb.set_trace()

    def test_post_many(self):
        response = self.client.get('/')
        ipdb.set_trace()

    def test_post_fail(self):
        tevents = ([
        ])
        response = self.client.post('/')
        ipdb.set_trace()

    def test_get_single(self):
        ipdb.set_trace()
        for n in self.fdata['events']:
            response = self.client.get(f'/{n}/')
            assert(response.status_code == 200)

    def test_get_fail(self):
        n = len(self.fdata['events']) + 1
        response = self.client.get(f'/{n}/')
        assert(response.status == 404)
        ipdb.set_trace()

    def test_patch_add(self):
        response = self.client.get('/')
        ipdb.set_trace()

    def test_patch_empty(self):
        for n in self.fdata['events']:
            response = self.client.patch(f'/{n}/', {'span': []})
            assert(response.status_code == 200)
            assert(len(response.content) == 0)
        ipdb.set_trace()

    def test_patch_fail(self):
        response = self.client.patch('/1/', {'parties': []})
        ipdb.set_trace()
        response = self.client.patch('/1/', {'span': {'break': 'foo'}})

    def test_delete(self):
        self

    def test_delete_fail(self):
        # ?
        assert(True)

    #
    def test_list_auth(self):
        self

    def test_post_auth_fail(self):
        self

    def test_get_auth_fail(self):
        self

    def test_patch_auth_fail(self):
        self

    def test_delete_auth_fail(self):
        self
