import json
from pathlib import Path
from ipdb import set_trace as st

from django.test import tag, override_settings
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries

from schedul.models import Event, TimeSpan
from schedul.serializers import EventSerializer, TimeSpanSerializer
from .views import EventList, EventDetail

from rest_framework.test import (
    APIRequestFactory, APITestCase, 
    APILiveServerTestCase, URLPatternsTestCase,
    force_authenticate,
    RequestsClient
)

#from django.db import connection
from django.conf import settings
import ipdb

# x csrf, auth x env, logging
# email, m/t q

if True:
#if False:
    def st(*args, **kwargs):
        pass

def print_queries():
    print(json.dumps(connection.queries, indent=2), len(connection.queries))


from inspect import currentframe, getframeinfo
def append_qlog(self, frame=None):
    frameinfo = getframeinfo(frame or currentframe())
    qlog_path = 'qlog'
    nym = self._testMethodName if hasattr(self, '_testMethodName') else frameinfo.function
    with open(qlog_path, 'a') as fd:
        fd.write('=== ' + nym + '\n')
        fd.write(json.dumps(connection.queries, indent=2))
        fd.write('\n' + str(len(connection.queries)) + '=== \n/' + nym + '\n\n')


def map_fixtures(fixtures):
    #
    bpath = Path(__file__).resolve().parent / 'fixtures'
    fdata = {}
    for f in fixtures:
        fpath = bpath / (f + '.json')
        with open(fpath) as fd:
            fdata[f] = json.loads(fd.read())
    ev = ([x['pk'] for x in fdata['schedul']
            if x['model'] == 'schedul.event'])
    ep = ([x['fields']['parties'] for x in fdata['schedul'] 
        if x['model'] == 'schedul.event'])
    uu = [x['pk'] for x in fdata['users']]
    return {
        'slots': ([(x['fields']['begin'], x['fields']['duration']) 
            for x in fdata['schedul'] 
            if x['model'] == 'schedul.timespan']),
        'emails': [x['fields']['email'] for x in fdata['users']],
        'staff': [x['fields']['is_staff'] for x in fdata['users']],
        'active': [x['fields']['is_active'] for x in fdata['users']],
        'users': uu,#[x['pk'] for x in fdata['users']],
        'events': ev,#([x['pk'] for x in fdata['schedul']
            #if x['model'] == 'schedul.event']),
        'uevents':[[x[0] for x in zip(ev,ep) if y in x[1]] for y in uu],
        'eventp': ep,
        #'data': fdata
    }
    # X: doubly munging spans?
    #   add dummy spans ?

class EventViewTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.factory = APIRequestFactory()
        #cls.factory = APIRequestFactory(enforce_csrf_checks=True)
        st()

    @classmethod
    def setUpTestData(cls):
        print(cls.fixtures)
        cls.fdata = map_fixtures(cls.fixtures)
        User = get_user_model()
        cls.suser = User.objects.create(username='sup', #is_superuser=True,
            is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()
        st()



    def setUp(self):
        #cls.client.enforce_csrf_checks = True # only login, not force

        print(self._testMethodName)

        print('a', self.client.session.items(), len(connection.queries))
        settings.DEBUG = True
        print('b', self.client.session.items(), len(connection.queries))

        self.client.login(username='sup', password='p')

        print('c', self.client.session.items(), len(connection.queries))
        append_qlog(self)
        reset_queries()
        #st()

    def tearDown(self):
        append_qlog(self)

    def get_slots(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['slots'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]


    #
    def test_list_get(self):
        st()

        # X: to setUp/Class
        # X: override/modify_settings + default_format
        #settings.DEBUG = True

        response = self.client.get('/')
        print('cq', len(connection.queries))

        request = self.factory.get('/')
        aview = EventList.as_view()
        request.user = self.suser
        #force_authenticate(request, user=self.suser)
        ipdb; ipdb.set_trace()
        arsp = aview(request)
        #y = view.setup(request)

        bview = EventList()
        z = bview.setup(request)
        brsp = bview.get(request)
        print(request, arsp, brsp, len(connection.queries))#view.get_context_data())
        st()

        #print(response.content)
        print('cq', len(connection.queries))
        self.assertTrue(response.status_code == 200)
        jc = json.loads(response.content)
        #print(jc, len(jc), len(self.fdata['events']))
        self.assertEqual(len(jc), len(self.fdata['events']))
        st()

    def test_list_post(self):
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        self.assertEqual(response.status_code, 201)
        #print(response.data['slots'], response.data['parties'])
        print('cq', len(connection.queries))
        st()

    def test_list_post_many_fail(self):
        tevents = ([{
                'parties': self.get_parties(0, len(self.fdata['emails'])),
                'slots': self.get_slots(0, 1)
            },
            {
                'parties': self.get_parties(0, 1),
                'slots': self.get_slots(0, len(self.fdata['slots']))
        }])
        response = self.client.post('/', tevents, format='json')
        print('cq', len(connection.queries))
        #print(response)
        self.assertEqual(response.status_code, 400)
        #st()

    def test_list_post_fail(self):
        response = self.client.post('/')
        print('cq', len(connection.queries))
        self.assertEqual(response.status_code, 400)
        st()
        # X: errs on both? no matter what
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails']))
        })
        print('cq', len(connection.queries))
        print(response)
        response = self.client.post('/', {
            'parties': [],
            'slots': self.get_slots(0, len(self.fdata['slots']))
        })
        print('cq', len(connection.queries))
        print(response)
        st()


    def test_detail_get(self):
        for n in self.fdata['events']:
            response = self.client.get(f'/{n}/')
            self.assertTrue(response.status_code == 200)
            print('cq', len(connection.queries))
        print('cq', len(connection.queries))

    def test_detail_get_fail(self):
        n = len(self.fdata['events']) + 1
        #st()
        response = self.client.get(f'/{n}/')
        self.assertTrue(response.status_code == 404)
        print('cq', len(connection.queries))


    def test_detail_patch_add(self):
        #return
        print('precq', len(connection.queries))
        for n in self.fdata['events']:
            print('acq', len(connection.queries))
            resp = self.client.patch(f'/{n}/', {
                'slots': self.get_slots(0, len(self.fdata['slots'])),
            }, format='json')
            st()
            print(
                len(resp.data['slots']), len(self.fdata['slots'])
            )
            print('bcq', len(connection.queries))
        print('postcq', len(connection.queries))

    def test_detail_patch_empty(self):
        for n in self.fdata['events']:
            response = self.client.patch(f'/{n}/', {'slots': []},
                format='json')
            st()
            self.assertTrue(response.status_code == 202)
            #assert(len(response.content) == 0)
            jc = json.loads(response.content)
            print(n, jc, len(jc['slots']))
            print('cq', len(connection.queries))
        print('cq', len(connection.queries))

    def test_detail_patch_fail(self):
        st()
        #with self.assertRaises(AssertionError):
        #    response = self.client.patch('/2/', {'parties': []})

        # X: custom valid err - prior to mprenderer ..
        # X: format='json' or settings...
        response = self.client.patch('/2/', {'parties': []})
        print('cq', len(connection.queries))
        #print(response.data)
        self.assertTrue(response.status_code == 400)
        st()

        with self.assertRaises(AssertionError):
            # X: custom valid err - after mprenderer ..
            response = self.client.patch('/1/', {'slots': {'break': 'foo'}})
            self.assertTrue(response.status_code == 400)
        #print(response.content)
        print('cq', len(connection.queries))
        st()


    def test_detail_delete(self):
        self

    def test_detail_delete_fail(self):
        # ?
        self.assertTrue(True)


@tag('dispatch')
class DispatchViewTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.fdata = map_fixtures(cls.fixtures)
        st()

    def test_notify_get(self):
        self

    def test_notify_post(self):
        self
    def test_notify_post_fail(self):
        self

    def test_log_get(self):
        self
    
    def test_list_post_update(self):
        self
    
    def test_list_get_token_update(self):
        self

    def test_detail_get_viewed(self):
        self    


@tag('auth')
class ViewAuthTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.fdata = map_fixtures(cls.fixtures)
        st()
    #

    def setUp(self):
        pass

    def map_expects(self, uidx):
        self.edata = dict(
            list_get=[],
            list_post=[]
        )

    def test_list_get_auth(self):
        self
        for i in range(len(self.fdata['users'])):
            pass


    def test_list_post_auth_fail(self):
        self
    
    def test_detail_get_auth_fail(self):
        # user not in parties, user not is_active
        self

    def test_detail_patch_auth_fail(self):
        self

    def test_detail_delete_auth_fail(self):
        self

    def test_notify_get_auth_fail(self):
        self

    def test_notify_post_auth_fail(self):
        self

    def test_log_get_auth_fail(self):
        self

    #def test_list_post_update_auth_fail(self):
    #def test_list_get_token_update_auth_fail(self):
    #def test_list_get_viewed_auth_fail(self):
    #test_detail_get_auth_fail(self):
    #test_detail_patch_auth_fail(self):

