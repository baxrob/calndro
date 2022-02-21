import json
from pathlib import Path
from unittest import skip
try:
    from ipdb import set_trace as st
except:
    from pdb import set_trace as st

#from django.conf import settings
from django.core import mail
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
        #return [{'email': x} for x in self.fdata['emails'][n:n+m]]
        return self.fdata['emails'][n:n+m]


    def test_openapi_get(self):
        resp = self.client.get('/openapi')
        self.assertEqual(resp.status_code, 200)

    def test_openapi_get_fail(self):
        resp = self.client.get('/openapi/')
        self.assertEqual(resp.status_code, 404)

    def test_detail_get(self):
        for n in self.fdata['events']:
            resp = self.client.get(f'/{n}/')
            self.assertEqual(resp.status_code, 200)

    def test_detail_get_fail(self):
        n = len(self.fdata['events']) + 1
        resp = self.client.get(f'/{n}/')
        self.assertEqual(resp.status_code, 404)

    def test_detail_patch_dupe(self):
        # todo-
        # X: redundant loop
        for n in self.fdata['events']:
            resp1 = self.client.get(f'/{n}/')
            slots = resp1.data['slots'] + resp1.data['slots']
            resp2 = self.client.patch(f'/{n}/', {'slots': slots},
                format='json')
            self.assertEqual(
                len(resp1.data['slots']), len(resp2.data['slots']))

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
            #'parties': [{'email': e} for e in emails],
            'parties': emails,
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
        #return [{'email': x} for x in self.fdata['emails'][n:n+m]]
        return self.fdata['emails'][n:n+m]

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
        # todo-
        # check: not in event and not staff, not active
        # X: alternatively, loop users/evts and skip valid/deleting
        failu = []
        for eidx, eid in enumerate(self.fdata['events']):
            u1 = [uu for u, uu in enumerate(self.fdata['users'])
                if uu not in self.fdata['eventp'][eidx]
                    and not self.fdata['staff'][u]
                    and self.fdata['active'][u]
            ]
            u2 = [uu for u, uu in enumerate(self.fdata['users'])
                if not self.fdata['active'][u]
            ]
            failu.append([u1, u2])
        #import ipdb; ipdb.set_trace()
        for idx, failers in enumerate(failu):
            evt_id = self.fdata['events'][idx]
            for uid in failers[0]:
                user = User.objects.get(pk=uid)
                self.client.force_login(user)
                resp = self.client.delete(f'/{evt_id}/')
                self.assertEqual(resp.status_code, 403)
            for uid in failers[1]:
                user = User.objects.get(pk=uid)
                self.client.force_login(user)
                resp = self.client.delete(f'/{evt_id}/')
                self.assertEqual(resp.status_code, 403)

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
        # X: get and notify as suser - for each userXevent
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
                #u_eml = {'email': self.fdata['emails'][ur_idx]}
                u_eml = self.fdata['emails'][ur_idx]

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
                #st()

                # X: 
                #for m in mail.outbox:
                #    print(vars(m))

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
        #
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)
        resp = self.client.post('/', {'parties': [token_user], 'slots': []},
            format='json')
        evt_id = resp.data['id']
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [token_user],
            #'slots': [], 'sender': {'email': suser.email}}, format='json') 
            'slots': [], 'sender': token_user}, format='json') 
        self.client.logout()
        return evt_id


    def test_detail_get_emailtoken(self):
        #evt_id = self.fdata['events'][0]

        # X: this sh* - updy tests and fix srz.to_internal ? 
        #ur_eml = {'email': 'nonesuch@localhost'}
        ur_eml = 'nonesuch@localhost'

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

        #userr = User.objects.get(email=ur_eml['email'])
        userr = User.objects.get(email=ur_eml)
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
        # user*3 : mismatch : ut et -- no, logged in user would be ignored
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)

        #ur1_eml = {'email': 'nonesuch@localhost'}
        #ur2_eml = {'email': 'nohownil@localhost'}
        ur1_eml = 'nonesuch@localhost'
        ur2_eml = 'nohownil@localhost'
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

        # X: redundant - user won't mismatch token since that identifies user
        #user1 = User.objects.get(email=ur1_eml['email'])
        #user2 = User.objects.get(email=ur2_eml['email'])
        user1 = User.objects.get(email=ur1_eml)
        user2 = User.objects.get(email=ur2_eml)
        tok1 = EmailToken.objects.get(user=user1, event_id=evt1_id).key
        tok2 = EmailToken.objects.get(user=user2, event_id=evt2_id).key
        #print(tok1, tok2)
        resp3 = self.client.get(f'/{evt2_id}/?et={tok1}')
        self.assertEqual(resp3.status_code, 403)
        resp4 = self.client.get(f'/{evt1_id}/?et={tok2}')
        self.assertEqual(resp4.status_code, 403)
        #print(resp3.data, resp4.data)

    def test_detail_patch_emailtoken(self):
        # todo-
        # X:
        #ur_eml = {'email': 'nonesuch@localhost'}
        ur_eml = 'nonesuch@localhost'
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)

        resp = self.client.post('/', {'parties': [ur_eml], 'slots': []},
            format='json')
        evt_id = resp.data['id']
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [ur_eml],
            'slots': [], 'sender': ur_eml}, format='json') 
        self.client.logout()

        #userr = User.objects.get(email=ur_eml['email'])
        userr = User.objects.get(email=ur_eml)
        tok = EmailToken.objects.get(user=userr, event_id=evt_id).key
        #resp = self.client.get(f'/{evt_id}/?et={tok}')
        resp = self.client.patch(f'/{evt_id}/?et={tok}', {'slots': []},
            format='json')
        self.assertEqual(resp.status_code, 202)

    def test_detail_patch_emailtoken_fail(self):
        # todo-
        ue = 'nonesuch@localhost'
        # X: 
        #tok_evt_id = self.setup_emailtoken({'email': ue})
        tok_evt_id = self.setup_emailtoken(ue)
        tok_user = User.objects.get(email=ue)
        #import ipdb; ipdb.set_trace()
        tok = EmailToken.objects.get(user=tok_user, event_id=tok_evt_id).key
        nevt_id = self.fdata['events'][0]
        resp = self.client.patch(f'/{nevt_id}/?et={tok}')
        self.assertEqual(resp.status_code, 403)

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

    def test_emailtoken_expired(self):
        # todo
        self.assertEqual



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
        #return [{'email': x} for x in self.fdata['emails'][n:n+m]]
        return self.fdata['emails'][n:n+m]


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
        # todo-
        # X: presumes u1 in e1 - should get uevents[0][0]
        evt_id = self.fdata['events'][0]
        evt_id = self.fdata['uevents'][0][0]
        user_id = self.fdata['users'][0]
        user = User.objects.get(pk=user_id)
        #u_eml = {'email': user.email}
        u_eml = user.email
        resp = self.client.get(f'/{evt_id}/')
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [u_eml],
            'slots': resp.data['slots'], 'sender': u_eml}, format='json') 
        print(mail.outbox[0].subject)
        mm = mail.outbox[0]
        print(vars(mm))
        #st()
        self.assertEqual(resp.status_code, 202)

        #
        self.assertEqual(len(mail.outbox), 1)

    def test_notify_post_fail(self):
        # todo-
        # parties, eml, slots, dt
        # sender not in evt, party/s not in evt, slots mismatch
        users = []
        evt_ids = []
        user_ids = self.fdata['users']
        for uidx, uid in enumerate(user_ids):
            email = self.fdata['emails'][uidx]
            # X: ? use fixture - assumes covering pattern -- as above, coupling
            #resp = self.client.post('/', {'parties': [{'email': email}],
            resp = self.client.post('/', {'parties': [email],
                'slots': self.get_slots(0, len(self.fdata['slots']))},
                format='json')
            evt_ids.append(resp.data['id'])
            evt_id = resp.data['id']
            slots = resp.data['slots']
            uidx_next = (uidx + 1) % len(user_ids)
            email_next = self.fdata['emails'][uidx_next]
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                #[{'email': email}], 'slots': slots, 
                #'sender': {'email': email_next}},
                [email], 'slots': slots, 
                'sender': email_next},
                format='json')
            #print(resp, email, email_next, resp.data)
            #print(resp.data)
            self.assertEqual(resp.status_code, 400)
            #st()
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                #[{'email': email_next}], 
                #[{'email': email_next}, {'email': 'limbo@localhost'}],
                [email_next, 'limbo@localhost'],
                'slots': slots, 'sender': 
                #{'email': email}}, format='json')
                email}, format='json')
            #print(resp, email_next, email, resp.data)
            #print(resp.data)
            self.assertEqual(resp.status_code, 400)
            slots.pop()
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                #[{'email': email}], 'slots': slots, 'sender': 
                #{'email': email}}, format='json')
                [email], 'slots': slots, 'sender': 
                email}, format='json')
            #print(resp.data)
            self.assertEqual(resp.status_code, 400)



    def test_notify_post_lognotify(self):
        # todo-
        self.assertEqual
        evt_id = self.fdata['events'][0]
        user_id = self.fdata['users'][0]
        user = User.objects.get(pk=user_id)
        #u_eml = {'email': user.email}
        u_eml = user.email
        resp = self.client.get(f'/{evt_id}/')
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [u_eml],
            'slots': resp.data['slots'], 'sender': u_eml}, format='json') 
        resp = self.client.get(f'/{evt_id}/log/')
        #st()
        self.assertEqual(resp.data['entries'][-1]['occurrence'], 'NOTIFY')

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
        #print(resp.data)
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
        print(len(connection.queries))
        self.client.login(username='sup', password='p')
        print(len(connection.queries))
        self.assertEqual
        reset_queries()
        print(len(connection.queries))

    def get_slots(self, n=0, m=1):
        return ([{'begin': x[0], 'duration': x[1]}
            for x in self.fdata['slots'][n:n+m]])

    def get_parties(self, n=0, m=1):
        #return [{'email': x} for x in self.fdata['emails'][n:n+m]]
        return self.fdata['emails'][n:n+m]

        
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
