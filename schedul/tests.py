import json
from pathlib import Path
from ipdb import set_trace as st

from django.test import tag
from django.contrib.auth import get_user_model

from schedul.models import Event, TimeSpan
from schedul.serializers import EventSerializer, TimeSpanSerializer
from .views import EventList, EventDetail

from rest_framework.test import (
    APIRequestFactory, APITestCase, 
    APILiveServerTestCase, URLPatternsTestCase,
    force_authenticate,
    RequestsClient
)

# x csrf, auth x env, logging
# email, m/t q

# requestfactory, numqueries

if True:
#if False:
    def st(*args, **kwargs):
        pass

def map_fixtures(fixtures):
    fdata = {}
    bpath = Path(__file__).resolve().parent / 'fixtures'
    fdata = {}
    for f in fixtures:
        fpath = bpath / (f + '.json')
        with open(fpath) as fd:
            fdata[f] = json.loads(fd.read())
    return {
        'spans': ([(x['fields']['begin'], x['fields']['duration']) 
            for x in fdata['schedul'] 
            if x['model'] == 'schedul.timespan']),
        'emails': [x['fields']['email'] for x in fdata['users']],
        'users': [x['pk'] for x in fdata['users']],
        'events': ([x['pk'] for x in fdata['schedul']
            if x['model'] == 'schedul.event']),
        'data': fdata
    }
    # X: doubly munging spans?
    #   add dummy spans ?

class EventTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.fdata = map_fixtures(cls.fixtures)
        User = get_user_model()
        cls.suser = User.objects.create(username='sup', is_superuser=True)
        cls.suser.set_password('p')
        cls.suser.save()
        cls.factory = APIRequestFactory()
        #cls.factory = APIRequestFactory(enforce_csrf_checks=True)
        st()

    @classmethod
    def setUpTestData(cls):
        st()

    def setUp(self):
        #cls.client.enforce_csrf_checks = True # only login, not force

        #print(self.fixtures)
        #print(self.fdata)
        #st()
        print(self._testMethodName)

        print(self.client.session.items())
        self.client.login(username='sup', password='p')
        #st()

    def get_spans(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['spans'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]


    #
    @tag('list', 'get')
    def test_get_list(self):
        st()
        from django.db import connection

        response = self.client.get('/')
        print(connection.queries, len(connection.queries))

        request = self.factory.get('/')
        aview = EventList.as_view()
        request.user = self.suser
        #force_authenticate(request, user=self.suser)
        arsp = aview(request)
        #y = view.setup(request)

        bview = EventList()
        z = bview.setup(request)
        brsp = bview.get(request)
        print(request, arsp, brsp, connection.queries)#view.get_context_data())
        st()

        print(response.content)
        self.assertTrue(response.status_code == 200)
        jc = json.loads(response.content)
        print(jc, len(jc), len(self.fdata['events']))
        self.assertEqual(len(jc), len(self.fdata['events']))
        st()

    @tag('list', 'post')
    def test_post_single(self):
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'span': self.get_spans(0, len(self.fdata['spans']))
        }, format='json')
        self.assertEqual(response.status_code, 201)
        print(response.data['span'], response.data['parties'])
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
        self.assertEqual(response.status_code, 400)
        st()
        # X: errs on both? no matter what
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
        st()
        return
        for n in self.fdata['events']:
            resp = self.client.patch(f'/{n}/', 
                self.get_spans(0, len(self.fdata.spans)),
                format='json')
            print(
                len(resp.content['spans']), len(self.fdata.spans)
            )

    @tag('detail', 'patch')
    def test_patch_empty(self):
        for n in self.fdata['events']:
            response = self.client.patch(f'/{n}/', {'span': []},
                format='json')
            assert(response.status_code == 200)
            #assert(len(response.content) == 0)
            jc = json.loads(response.content)
            print(n, jc, len(jc['span']))

    @tag('detail', 'patch', 'fail')
    def test_patch_fail(self):
        st()
        #with self.assertRaises(AssertionError):
        #    response = self.client.patch('/2/', {'parties': []})

        # X: custom valid err - prior to mprenderer ..
        response = self.client.patch('/2/', {'parties': []})
        print(response.data)
        st()

        with self.assertRaises(AssertionError):
            # X: custom valid err - after mprenderer ..
            response = self.client.patch('/1/', {'span': {'break': 'foo'}})
        print(response.content)
        st()


    @tag('detail', 'delete')
    def test_delete(self):
        self

    @tag('detail', 'delete', 'fail')
    def test_delete_fail(self):
        # ?
        self.assertTrue(True)


@tag('auth')
class AuthTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.fdata = map_fixtures(cls.fixtures)
        st()
    #

    def setUp(self):
        pass

    def map_expects(self):
        pass

    @tag('list', 'get', 'post')
    def test_list_auth(self):
        self

    @tag('list', 'post', 'fail')
    def test_post_auth_fail(self):
        self
    
    @tag('detail', 'get', 'fail')
    def test_get_auth_fail(self):
        self

    @tag('detail', 'patch', 'fail')
    def test_patch_auth_fail(self):
        self

    @tag('detail', 'delete', 'fail')
    def test_delete_auth_fail(self):
        self

