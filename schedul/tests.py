import json
from pathlib import Path
import ipdb
from ipdb import set_trace as st

from django.test import tag

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
        st()

    def setUp(self):
        #print(self.fixtures)
        #print(self.fdata)
        self.assertTrue(True)

    def get_spans(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['spans'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]


    #
    @tag('list', 'get')
    def test_get_list(self):
        st()
        response = self.client.get('/')
        print(response.content)
        self.assertTrue(response.status_code == 200)
        jc = json.loads(response.content)
        print(jc, len(jc))

    @tag('list', 'post')
    def test_post_single(self):
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'span': self.get_spans(0, len(self.fdata['spans']))
        }, format='json')
        self.assertEqual(response.status_code, 201)
        st()

    @tag('list', 'post')
    def test_post_many(self):
        tevents = ([{
                'parties': self.get_parties(0, len(self.fdata['emails'])),
                'span': self.get_spans(0, 1)
            },
            {
                'parties': self.get_parties(0, 1),
                'span': self.get_spans(0, len(self.fdata['spans']))
        }])
        response = self.client.post('/', tevents, format='json')
        print(response)
        self.assertEqual(response.status_code, 400)
        st()

    @tag('list', 'post', 'fail')
    def test_post_fail(self):
        response = self.client.post('/')
        st()
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails']))
        })
        print(response)
        response = self.client.post('/', {
            'parties': [],
            'span': self.get_spans(0, len(self.fdata['spans']))
        })
        print(response)
        st()


    @tag('detail', 'get')
    def test_get_single(self):
        st()
        for n in self.fdata['events']:
            response = self.client.get(f'/{n}/')
            assert(response.status_code == 200)

    @tag('detail', 'get', 'fail')
    def test_get_fail(self):
        n = len(self.fdata['events']) + 1
        response = self.client.get(f'/{n}/')
        st()
        assert(response.status_code == 404)


    @tag('detail', 'patch')
    def test_patch_add(self):
        response = self.client.get('/')
        st()

    @tag('detail', 'patch')
    def test_patch_empty(self):
        st()
        for n in self.fdata['events']:
            response = self.client.patch(f'/{n}/', {'span': []},
                format='json')
            assert(response.status_code == 200)
            #assert(len(response.content) == 0)
            jc = json.loads(response.content)
            print(jc, len(jc))

    @tag('detail', 'patch', 'fail')
    def test_patch_fail(self):
        st()
        #with self.assertRaises(AssertionError):
        #    response = self.client.patch('/2/', {'parties': []})
        with self.assertRaises(AssertionError) as fff:
            response = self.client.patch('/2/', {'parties': []})
        st()
        #with self.assertRaises(AssertionError):
        response = self.client.patch('/1/', {'span': {'break': 'foo'}})
        print(response.content)


    @tag('detail', 'delete')
    def test_delete(self):
        self

    @tag('detail', 'delete', 'fail')
    def test_delete_fail(self):
        # ?
        self.assertTrue(True)


    #
    @tag('list', 'get', 'post', 'auth')
    def test_list_auth(self):
        self

    @tag('list', 'post', 'auth', 'fail')
    def test_post_auth_fail(self):
        self
    
    @tag('detail', 'get', 'auth', 'fail')
    def test_get_auth_fail(self):
        self

    @tag('detail', 'patch', 'auth', 'fail')
    def test_patch_auth_fail(self):
        self

    @tag('detail', 'delete', 'auth', 'fail')
    def test_delete_auth_fail(self):
        self

