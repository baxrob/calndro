import json
from pathlib import Path
from ipdb import set_trace as st

#from django.conf import settings
from django.test import tag, override_settings
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from rest_framework.test import APITestCase

if True:
#if False:
    def st(*args, **kwargs):
        pass
    def print(*args, **kwargs):
        pass

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
        'users': uu,
        'events': ev,
        'uevents':[[x[0] for x in zip(ev,ep) if y in x[1]] for y in uu],
        'eventp': ep,
        #'data': fdata
    }


class EventViewTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpTestData(cls):
        cls.fdata = map_fixtures(cls.fixtures)
        User = get_user_model()
        cls.suser = User.objects.create(username='sup', #is_superuser=True,
            is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()

    def setUp(self):
        print(self._testMethodName)
        self.client.login(username='sup', password='p')

    def get_slots(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['slots'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]


    def test_detail_get(self):
        for n in self.fdata['events']:
            resp = self.client.get(f'/{n}/')
            self.assertTrue(resp.status_code == 200)

    def test_detail_get_fail(self):
        n = len(self.fdata['events']) + 1
        resp = self.client.get(f'/{n}/')
        self.assertTrue(resp.status_code == 404)

    def test_detail_patch_add(self):
        for n in self.fdata['events']:
            resp = self.client.patch(f'/{n}/', {
                'slots': self.get_slots(0, len(self.fdata['slots'])),
            }, format='json')
            self.assertTrue(resp.status_code == 202)
            self.assertTrue(
                len(resp.data['slots']) == len(self.fdata['slots']))

    def test_detail_patch_empty(self):
        for n in self.fdata['events']:
            resp = self.client.patch(f'/{n}/', {'slots': []},
                format='json')
            print(resp.data)
            self.assertTrue(resp.status_code == 202)
            self.assertTrue(len(resp.data['slots']) == 0)

    def test_detail_patch_parties_ignored(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/')
        p_a = len(resp.data['parties'])
        resp = self.client.patch(f'/{n}/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'slots': []
        }, format='json')
        resp = self.client.get(f'/{n}/')
        p_b = len(resp.data['parties'])
        self.assertTrue(p_a == p_b)
        resp = self.client.patch(f'/{n}/', {
            'parties': [],
            'slots': []
        }, format='json')
        resp = self.client.get(f'/{n}/')
        p_c = len(resp.data['parties'])
        self.assertTrue(p_a == p_c)

    def test_detail_patch_fail(self):
        n = self.fdata['events'][0]
        resp = self.client.patch(f'/{n}/', {'parties': []}, format='json')
        self.assertTrue(resp.status_code == 400)
        print(resp.data)
        resp = self.client.patch(f'/{n}/', {'slots': [{
                'begin': '2021-asdfT14:58:26.611000Z', 
                'duration': 'zy0:00:01'}]
            },
            format='json')
        print(resp.data)
        self.assertTrue(resp.status_code == 400)
        # rather pointless
        with self.assertRaises(AssertionError):
            resp = self.client.patch(f'/{n}/', {'slots': {'break': 'foo'}})
            self.assertTrue(resp.status_code == 400)
        print(resp.data)
        resp = self.client.patch(f'/{n}/', {'slots': {'break': 'foo'}},
            format='json')
        print(resp.data)
        self.assertTrue(resp.status_code == 400)

    def test_list_get(self):
        resp = self.client.get('/')
        self.assertTrue(resp.status_code == 200)
        self.assertTrue(len(resp.data) == len(self.fdata['events']))

    def test_list_get_fail(self):
        #
        pass

    def test_list_post(self):
        response = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_list_post_fail(self):
        # X: x format='json' - note field error before multipart invalid
        resp = self.client.post('/')
        self.assertEqual(resp.status_code, 400)
        #st()
        resp = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails']))
        })
        print(resp, resp.data)
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post('/', {
            'parties': [],
            'slots': self.get_slots(0, len(self.fdata['slots']))
        })
        print(resp, resp.data)
        self.assertEqual(resp.status_code, 400)
        # X: multi-event, malformed email, malformed dtime

    def test_detail_delete(self):
        n = self.fdata['events'][0]
        resp = self.client.delete(f'/{n}/')
        self.assertTrue(resp.status_code == 204)


@tag('auth')
class ViewAuthTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.fdata = map_fixtures(cls.fixtures)

    def setUp(self):
        print(self._testMethodName)

    def get_slots(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['slots'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]

    def loop_user_event_tests(self, method, path='', payload=None, 
        succ_code=200, fail_code=403):
        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]
            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
            self.client.force_login(user)
            for evt_id in self.fdata['events']:
                #resp = self.client.get(f'/{evt_id}/')
                resp = eval('self.client.' + method)(f'/{evt_id}/{path}',
                    payload, format='json')
                print(resp)
                is_staff = self.fdata['staff'][uidx]
                #if user.is_active and evt_id in uevts or user.is_staff:
                if user.is_active and evt_id in uevts or is_staff:
                    self.assertTrue(resp.status_code == succ_code)
                else:
                    self.assertTrue(resp.status_code == fail_code)


    def test_detail_get_auth_fail(self):
        self.loop_user_event_tests('get')

    def test_detail_patch_auth_fail(self):
        self.loop_user_event_tests('patch', '', {'slots': []}, 202, 403)

    def test_detail_delete_auth_fail(self):
        #
        self.assertTrue
        #st()
        #self.loop_user_event_tests('delete', succ_code=204)
        for uidx in range(len(self.fdata['users'])):
            pass

    def test_list_get_auth(self):
        for uidx in range(len(self.fdata['users'])):
            pass
            uid = self.fdata['users'][uidx]
            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
            self.client.force_login(user)
            pass
            evt_id = self.fdata['events'][0]
            resp = self.client.get('/', format='json')
            print(user, resp)
            is_staff = self.fdata['staff'][uidx]
            if user.is_active:
                #if evt_id in uevts or is_staff:
                if is_staff:
                    #self.assertTrue(resp.status_code == 201)
                    self.assertTrue(len(resp.data) == len(self.fdata['events']))
                else:
                    #self.assertTrue(resp.status_code == 403)
                    self.assertTrue(len(resp.data) == len(uevts))
            else:
                self.assertTrue(resp.status_code == 403)

    def test_list_post_auth_fail(self):
        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]
            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
            self.client.force_login(user)
            #pass
            #evt_id = self.fdata['events'][0]
            payload = {
                'parties': self.get_parties(0, len(self.fdata['emails'])),
                'slots': self.get_slots(0, len(self.fdata['slots']))
            }
            resp = self.client.post('/', payload, format='json')
            #print(user, resp, resp.data)#['id'])
            #st()
            #evt_id = resp.data['id']
            #is_staff = self.fdata['staff'][uidx]
            #st()
            if user.is_active: # and evt_id in uevts or is_staff:
                self.assertTrue(resp.status_code == 201)
            else:
                self.assertTrue(resp.status_code == 403)

    def test_notify_get_auth_fail(self):
        self.loop_user_event_tests('get', 'notify/')

    def test_notify_post_auth_fail(self):
        #
        self

    def test_log_get_auth_fail(self):
        self.loop_user_event_tests('get', 'log/')
    
    #def test_list_post_update_auth_fail(self):
    #def test_list_get_token_update_auth_fail(self):
    #def test_list_get_viewed_auth_fail(self):



@tag('dispatch')
class DispatchViewTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.fdata = map_fixtures(cls.fixtures)
        User = get_user_model()
        cls.suser = User.objects.create(username='sup', #is_superuser=True,
            is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()

    def setUp(self):
        print(self._testMethodName)
        self.client.login(username='sup', password='p')

    def get_slots(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['slots'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]


    def test_log_get(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        self.assertTrue(resp.status_code == 200)

    def test_log_get_fail(self):
        pass
    
    def test_notify_get(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/notify/')
        self.assertTrue(resp.status_code == 200)

    def test_notify_post(self):
        self

    def test_notify_post_fail(self):
        self

    def test_detail_get_viewed(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        resp = self.client.get(f'/{n}/')
        resp = self.client.get(f'/{n}/log/')
        len_b = len(resp.data['entries'])
        self.assertTrue(len_a + 1 == len_b)

    def test_detail_patch_update(self):
        n = self.fdata['events'][0]
    
    def test_detail_get_token_update(self):
        #
        self.assertTrue(True)

    def test_list_post_update(self):
        resp = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        n = resp.data['id']
        resp = self.client.get(f'/{n}/log/')
        self.assertTrue(len(resp.data['entries']) == 1)


@tag('queries')
@override_settings(DEBUG=True)
class ViewQueryTests(APITestCase):
    fixtures = ['users', 'schedul']

    @classmethod
    def setUpTestData(cls):
        cls.fdata = map_fixtures(cls.fixtures)
        User = get_user_model()
        cls.suser = User.objects.create(username='sup', #is_superuser=True,
            is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()

    def setUp(self):
        #print(self._testMethodName)
        self.client.login(username='sup', password='p')
        reset_queries()

    def get_slots(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['slots'][n:n+m]])

    def get_parties(self, n=0, m=1):
        return [{'email': x} for x in self.fdata['emails'][n:n+m]]

        
    def test_detail_get(self):
        self.assertTrue
    def test_detail_patch(self):
        self.assertTrue
    def test_list_get(self):
        self.assertTrue
    def test_list_post(self):
        self.assertTrue
    def test_detail_delete(self):
        self.assertTrue
    def test_log_get(self):
        self.assertTrue
    def test_notify_get(self):
        self.assertTrue
    def test_notify_post(self):
        self.assertTrue
    def test_list_post_update(self):
        self.assertTrue
    def test_list_get_token_update(self):
        #
        self.assertTrue
        self.assertTrue
