import json
from pathlib import Path
from unittest import skip
from ipdb import set_trace as st

#from django.conf import settings
from django.test import tag, override_settings
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from rest_framework.test import APITestCase

from schedul.models import EmailToken

User = get_user_model()

#if True:
if False:
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
            self.assertEqual(resp.status_code, 200)

    def test_detail_get_fail(self):
        n = len(self.fdata['events']) + 1
        resp = self.client.get(f'/{n}/')
        self.assertEqual(resp.status_code, 404)

    def test_detail_patch_dupe(self):
        # todo
        self.assertEqual 

    def test_detail_patch_add(self):
        for n in self.fdata['events']:
            resp = self.client.patch(f'/{n}/', {
                'slots': self.get_slots(0, len(self.fdata['slots'])),
            }, format='json')
            self.assertEqual(resp.status_code, 202)
            self.assertEqual(
                len(resp.data['slots']), len(self.fdata['slots']))

    def test_detail_patch_empty(self):
        for n in self.fdata['events']:
            resp = self.client.patch(f'/{n}/', {'slots': []},
                format='json')
            #print(resp.data)
            self.assertEqual(resp.status_code, 202)
            self.assertEqual(len(resp.data['slots']), 0)

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
        self.assertEqual(p_a, p_b)
        resp = self.client.patch(f'/{n}/', {
            'parties': [],
            'slots': []
        }, format='json')
        resp = self.client.get(f'/{n}/')
        p_c = len(resp.data['parties'])
        self.assertEqual(p_a, p_c)

    def test_detail_patch_fail(self):
        n = self.fdata['events'][0]
        resp = self.client.patch(f'/{n}/', {'parties': []}, format='json')
        self.assertEqual(resp.status_code, 400)
        #print(resp.data)
        resp = self.client.patch(f'/{n}/', {'slots': [{
                'begin': '2021-asdfT14:58:26.611000Z', 
                'duration': 'zy0:00:01'}]
            },
            format='json')
        #print(resp.data)
        self.assertEqual(resp.status_code, 400)
        # rather pointless
        with self.assertRaises(AssertionError):
            resp = self.client.patch(f'/{n}/', {'slots': {'break': 'foo'}})
            self.assertEqual(resp.status_code, 400)
        #print(resp.data)
        resp = self.client.patch(f'/{n}/', {'slots': {'break': 'foo'}},
            format='json')
        #print(resp.data)
        self.assertEqual(resp.status_code, 400)

    def test_list_get(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), len(self.fdata['events']))

    def test_list_get_fail(self):
        # how?
        pass

    def test_list_post(self):
        resp = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_list_post_nonuserparty(self):
        emails = ['nonesuch@localhost', 'nilnil@localhost'] 
        resp = self.client.post('/', {
            'parties': [{'email': e} for e in emails],
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        for eml in emails:
            umatch = User.objects.filter(email=eml)
            #st()
            self.assertEqual(len(umatch), 1)
            self.assertFalse(umatch[0].is_active)

    def test_list_post_fail(self):
        # X: x format='json' - note field error before multipart invalid
        resp = self.client.post('/')
        self.assertEqual(resp.status_code, 400)
        #st()
        resp = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails']))
        })
        #print(resp, resp.data)
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post('/', {
            'parties': [],
            'slots': self.get_slots(0, len(self.fdata['slots']))
        })
        #print(resp, resp.data)
        self.assertEqual(resp.status_code, 400)
        # X: multi-event, malformed email, malformed dtime

    def test_detail_delete(self):
        n = self.fdata['events'][0]
        resp = self.client.delete(f'/{n}/')
        self.assertEqual(resp.status_code, 204)


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
                resp = eval('self.client.' + method)(f'/{evt_id}/{path}',
                    payload, format='json')
                is_staff = self.fdata['staff'][uidx]
                #if user.is_active and evt_id in uevts or user.is_staff:
                if user.is_active and evt_id in uevts or is_staff:
                    self.assertEqual(resp.status_code, succ_code)
                else:
                    self.assertEqual(resp.status_code, fail_code)


    def test_detail_get_auth_fail(self):
        self.loop_user_event_tests('get')

    def test_detail_patch_auth_fail(self):
        self.loop_user_event_tests('patch', '', {'slots': []}, 202, 403)

    def test_detail_delete_auth_fail(self):
        #
        self.assertEqual
        #st()
        #self.loop_user_event_tests('delete', succ_code=204)
        for uidx in range(len(self.fdata['users'])):
            # check: not in event and not staff, not active
            pass

    def test_list_get_auth(self):
        # X: abstract?
        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]
            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
            self.client.force_login(user)
            #evt_id = self.fdata['events'][0]
            resp = self.client.get('/', format='json')
            is_staff = self.fdata['staff'][uidx]
            if user.is_active:
                #if evt_id in uevts or is_staff:
                if is_staff:
                    #self.assertTrue(resp.status_code == 201)
                    self.assertEqual(len(resp.data), len(self.fdata['events']))
                else:
                    #self.assertTrue(resp.status_code == 403)
                    self.assertEqual(len(resp.data), len(uevts))
            else:
                self.assertEqual(resp.status_code, 403)

    def test_list_post_auth_fail(self):
        # X: abstract?
        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]
            #uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
            self.client.force_login(user)
            payload = {
                'parties': self.get_parties(0, len(self.fdata['emails'])),
                'slots': self.get_slots(0, len(self.fdata['slots']))
            }
            resp = self.client.post('/', payload, format='json')
            #evt_id = resp.data['id']
            #is_staff = self.fdata['staff'][uidx]
            if user.is_active: # and evt_id in uevts or is_staff:
                self.assertEqual(resp.status_code, 201)
            else:
                self.assertEqual(resp.status_code, 403)

    #def test_notify_get_auth_fail(self):
    #    self.loop_user_event_tests('get', 'notify/')

    def test_notify_post_auth_fail(self):
        # todo-
        # X: abstract
        # X: sender in event vs recipient in event
        # X: get and notify as suser - for each userZevent
        suser = User.objects.create(username='sup', is_staff=True)

        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]

            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
            
            for evt_id in self.fdata['events']:
                #resp = self.client.get(f'/{evt_id}/')
                #resp = eval('self.client.' + method)(f'/{evt_id}/{path}',
                #    payload, format='json')
                evt_idx = self.fdata['events'].index(evt_id)
                ur_id = self.fdata['eventp'][evt_idx][0]
                ur_idx = self.fdata['users'].index(ur_id)
                u_eml = {'email': self.fdata['emails'][ur_idx]}

                self.client.force_login(suser)
                resp = self.client.get(f'/{evt_id}/')
                
                #st()
                #print(evt_id, evt_idx, u_eml, resp.data)

                self.client.force_login(user)
                resp = self.client.post(f'/{evt_id}/notify/', {'parties':
                    [u_eml], 'slots': resp.data['slots'], 'sender': u_eml},
                    format='json') 
                #print(resp)
                is_staff = self.fdata['staff'][uidx]
                #if user.is_active and evt_id in uevts or user.is_staff:
                #print(resp, user.is_active, evt_id, uevts, is_staff)
                #print(resp.data)
                if user.is_active and evt_id in uevts or is_staff:
                    self.assertEqual(resp.status_code, 202)
                else:
                    self.assertEqual(resp.status_code, 403)

    def test_log_get_auth_fail(self):
        self.loop_user_event_tests('get', 'log/')
    
    #def test_list_post_logupdate_auth_fail(self):
    #def test_list_get_emailtoken_logupdate_auth_fail(self):
    #def test_list_get_logviewed_auth_fail(self):

    def setup_emailtoken(self, token_user):
        return self

    def test_detail_get_emailtoken(self):
        #evt_id = self.fdata['events'][0]

        ur_eml = {'email': 'nonesuch@localhost'}
        # X: helper
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)
        #uc_id = self.fdata['users'][0]
        #userc = User.objects.get(pk=uc_id)
        #st()
        resp = self.client.post('/', {'parties': [ur_eml], 'slots': []},
            format='json')
        evt_id = resp.data['id']
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [ur_eml],
            'slots': [], 'sender': ur_eml}, format='json') 
        self.client.logout()

        userr = User.objects.get(email=ur_eml['email'])
        #det = EmailToken(en, userr.id)
        #det.save()
        #tok = det.key
        #usrr = User.objects.get(unr)
        #self.client.force_login(userr)
        tok = EmailToken.objects.get(user=userr, event_id=evt_id).key
        resp = self.client.get(f'/{evt_id}/?et={tok}')
        #st()
        self.assertEqual(resp.status_code, 200)

    def test_detail_get_emailtoken_fail(self):
        # todo-
        # user*3 : mismatch : ut et
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)

        ur1_eml = {'email': 'nonesuch@localhost'}
        ur2_eml = {'email': 'nohownil@localhost'}
        resp = self.client.post('/', {'parties': [ur1_eml, ur2_eml],
            'slots': []}, format='json')
        evt1_id = resp.data['id']
        resp1 = self.client.post(f'/{evt1_id}/notify/', {'parties': [ur1_eml],
            'slots': [], 'sender': ur2_eml}, format='json') 

        resp = self.client.post('/', {'parties': [ur2_eml], 'slots': []},
            format='json')
        evt2_id = resp.data['id']
        resp2 = self.client.post(f'/{evt2_id}/notify/', {'parties': [ur2_eml],
            'slots': [], 'sender': ur2_eml}, format='json') 
        self.client.logout()

        user1 = User.objects.get(email=ur1_eml['email'])
        user2 = User.objects.get(email=ur2_eml['email'])
        tok1 = EmailToken.objects.get(user=user1, event_id=evt1_id).key
        tok2 = EmailToken.objects.get(user=user2, event_id=evt2_id).key
        #print(tok1, tok2)
        resp = self.client.get(f'/{evt2_id}/?et={tok1}')
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get(f'/{evt1_id}/?et={tok2}')
        self.assertEqual(resp.status_code, 403)

    def test_detail_patch_emailtoken(self):
        # todo-
        self.assertEqual
        ur_eml = {'email': 'nonesuch@localhost'}
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)

        resp = self.client.post('/', {'parties': [ur_eml], 'slots': []},
            format='json')
        evt_id = resp.data['id']
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [ur_eml],
            'slots': [], 'sender': ur_eml}, format='json') 
        self.client.logout()

        userr = User.objects.get(email=ur_eml['email'])
        tok = EmailToken.objects.get(user=userr, event_id=evt_id).key
        #resp = self.client.get(f'/{evt_id}/?et={tok}')
        resp = self.client.patch(f'/{evt_id}/?et={tok}', {'slots': []},
            format='json')
        self.assertEqual(resp.status_code, 202)

    def test_detail_patch_emailtoken_fail(self):
        # todo
        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]
            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
        self.assertEqual

    def test_notify_post_emailtoken(self):
        # todo
        self.assertTrue(True)

    def test_notify_post_emailtoken_fail(self):
        # todo
        for uidx in range(len(self.fdata['users'])):
            uid = self.fdata['users'][uidx]
            uevts = self.fdata['uevents'][uidx]
            user = get_user_model().objects.get(pk=uid)
        self.assertTrue(True)



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
        self.assertEqual(resp.status_code, 200)

    def test_log_get_fail(self):
        self.assertEqual
        n = len(self.fdata['events']) + 1
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(resp.status_code, 404)
    
    def test_notify_get(self):
        # nonesuch
        pass

    def test_notify_get_fail(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/notify/')
        #self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.status_code, 405)

    def test_notify_post(self):
        evt_id = self.fdata['events'][0]
        user_id = self.fdata['users'][0]
        user = User.objects.get(pk=user_id)
        u_eml = {'email': user.email}
        resp = self.client.get(f'/{evt_id}/')
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [u_eml],
            'slots': resp.data['slots'], 'sender': u_eml}, format='json') 
        #st()
        self.assertEqual(resp.status_code, 202)

    def test_notify_post_fail(self):
        # todo
        # parties, eml, slots, dt
        # sender not in evt, party/s not in evt, slots mismatch
        self

    def test_notify_post_logupdate(self):
        # todo
        self.assertEqual

    def test_detail_get_logviewed(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        resp = self.client.get(f'/{n}/')
        resp = self.client.get(f'/{n}/log/')
        len_b = len(resp.data['entries'])
        self.assertEqual(len_a + 1, len_b)
    
    def test_detail_get_emailtoken_logviewed(self):
        # todo
        # isn't this covered by ...get_logviewed
        self.assertTrue(True)

    def test_detail_patch_logupdate(self):
        n = self.fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        resp = self.client.patch(f'/{n}/', {
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(len(resp.data['entries']), len_a + 1)

    def test_list_post_logupdate(self):
        resp = self.client.post('/', {
            'parties': self.get_parties(0, len(self.fdata['emails'])),
            'slots': self.get_slots(0, len(self.fdata['slots']))
        }, format='json')
        n = resp.data['id']
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(len(resp.data['entries']), 1)


@skip
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
        self.assertEqual
    def test_detail_patch(self):
        self.assertEqual
    def test_list_get(self):
        self.assertEqual
    def test_list_post(self):
        self.assertEqual
    def test_detail_delete(self):
        self.assertEqual
    def test_log_get(self):
        self.assertEqual
    def test_notify_get(self):
        self.assertEqual
    def test_notify_post(self):
        self.assertEqual
    def test_list_post_update(self):
        self.assertEqual

    # X: scrap - can't get list with emailtoken
    def test_list_get_emailtoken_update(self):
        #
        self.assertEqual
        self.assertEqual
