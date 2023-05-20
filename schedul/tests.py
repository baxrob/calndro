import json
from pathlib import Path
from unittest import skip

try:
    from ipdb import set_trace as st
except:
    from pdb import set_trace as st

from datetime import datetime, timedelta
from django.utils import timezone

from django.core import mail
from django.test import tag, override_settings
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from rest_framework.test import APITestCase

from schedul.models import EmailToken
from schedul.fixtures import gen_sched

User = get_user_model()


import os
if 'DJTEST_QUIET' in os.environ:
    def st(*args, **kwargs):
        pass
    def print(*args, **kwargs):
        pass

fixture_files = ['users_dev', 'schedul']

def map_fixtures(fixtures):
    #
    bpath = Path(__file__).resolve().parent / 'fixtures'
    fdata = {}
    for f in fixtures:
        fpath = bpath / (f + '.json')
        # 
        f = 'users' if 'users' in f else 'schedul' if 'schedul' in f else f
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
    }

fdata = map_fixtures(fixture_files)

def get_slots(n=0, m=1):
    return ([{'begin': x[0], 'duration': x[1]}
        for x in fdata['slots'][n:n+m]])

def get_parties(n=0, m=1):
    return fdata['emails'][n:n+m]

def setup_emailtoken(self, token_user):
    #
    suser, created = User.objects.get_or_create(username='sup', is_staff=True)
    self.client.force_login(suser)
    resp = self.client.post('/', {'parties': [token_user], 'slots': []},
        format='json')
    evt_id = resp.data['id']
    resp = self.client.post(f'/{evt_id}/notify/', {'parties': [token_user],
        'slots': [], 'sender': token_user}, format='json') 
    self.client.logout()
    user = User.objects.get(email=token_user)
    tok = EmailToken.objects.get(user=user, event_id=evt_id).key
    return [evt_id, user, tok]

def fetch_log(self, evt_id):
    suser, created = User.objects.get_or_create(username='sup', is_staff=True)
    self.client.force_login(suser)
    resp = self.client.get(f'/{evt_id}/log/')
    self.client.logout()
    return resp.data['entries']


class EventViewTests(APITestCase):
    fixtures = fixture_files

    @classmethod
    def setUpTestData(cls):
        cls.suser = User.objects.create(username='sup', is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()

    def setUp(self):
        print(self._testMethodName)
        self.client.login(username='sup', password='p')


    def test_openapi_get(self):
        resp = self.client.get('/openapi')
        self.assertEqual(resp.status_code, 200)

    def test_openapi_get_fail(self):
        resp = self.client.get('/openapi/')
        self.assertEqual(resp.status_code, 404)


    def test_list_get(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), len(fdata['events']))

    def test_list_get_fail(self):
        resp = self.client.get('/foo')
        self.assertEqual(resp.status_code, 404)

    def test_list_post(self):
        resp = self.client.post('/', {
            'title': 'boofar',
            'parties': get_parties(0, len(fdata['emails'])),
            'slots': get_slots(0, len(fdata['slots']))
        }, format='json')
        self.assertEqual(resp.status_code, 201)

        # Empty slots
        resp = self.client.post('/', {
            'parties': get_parties(), 'slots': [],
        }, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_list_post_nonuserparty_created(self):
        emails = ['nonesuch@localhost', 'nilnil@localhost'] 
        resp = self.client.post('/', {
            'parties': emails,
            'slots': get_slots(0, len(fdata['slots']))
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        for eml in emails:
            umatch = User.objects.filter(email=eml)
            self.assertEqual(len(umatch), 1)
            self.assertFalse(umatch[0].is_active)

    @tag('todo')
    def test_list_post_fail(self):
        # todo
        #  parties not empty enforced

        # X: format='json' - note field error throws on top-level 
        #   dict attr before multipart invalid

        # X: mistest
        # Non-json format
        resp = self.client.post('/', {'parties': get_parties(), 'slots': []})
        self.assertEqual(resp.status_code, 400)

        # Missing slots
        resp = self.client.post('/', {
            'parties': get_parties(0, len(fdata['emails']))
        }, format='json')
        self.assertEqual(resp.status_code, 400)

        # todo-
        # Over maximum slots
        from django.conf import settings
        resp = self.client.post('/', {
            'parties': get_parties(),
            'slots': gen_sched.gen_slots([31])
        }, format='json')
        self.assertEqual(resp.status_code, 400)

        # Missing Parties
        resp = self.client.post('/', {
            'slots': []
        }, format='json')
        self.assertEqual(resp.status_code, 400)

        # Malformed slots - datetime
        resp = self.client.post('/', {
            'parties': get_parties(0, len(fdata['emails'])),
            'slots': [{
                'begin': '2021-asdfT14:58:26.611000Z', 
                'duration': 'zy0:00:01'}]
        }, format='json')
        self.assertEqual(resp.status_code, 400)

        # Malformed slots - dict
        resp = self.client.post('/', {
            'parties': get_parties(0, len(fdata['emails'])),
            'slots': {'bad': 'data'}
        }, format='json')
        self.assertEqual(resp.status_code, 400)

        # Non-json format
        resp = self.client.post('/', {
            'parties': get_parties(0, len(fdata['emails'])),
            'slots': []
        })
        self.assertEqual(resp.status_code, 400)

        # Non-json format, malformed slots - dict
        with self.assertRaises(AssertionError):
            resp = self.client.post('/', {
                'parties': get_parties(0, len(fdata['emails'])),
                'slots': {'bad': 'data'}
            })


    def test_detail_get(self):
        for n in fdata['events']:
            resp = self.client.get(f'/{n}/')
            self.assertEqual(resp.status_code, 200)

    def test_detail_get_noendslash_redirect(self):
        resp = self.client.get('/0')
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp.url, '/0/')

    def test_detail_get_fail(self):
        n = len(fdata['events']) + 1
        resp = self.client.get(f'/{n}/')
        self.assertEqual(resp.status_code, 404)


    @tag('todo')
    def test_detail_patch_title_change(self):
        # todo
        resp = self.client.get('/1/')
        oldtitle = resp.data['title']
        resp = self.client.patch('/1/', {'title': oldtitle+'newtitle'})
        #st()
        #self.assertTrue(resp.data['title'] == oldtitle+'newtitle')

    def test_detail_patch_add_slots(self):
        # X: presumes event fixtures vary in slot inclusion
        for n in fdata['events']:
            resp = self.client.patch(f'/{n}/', {
                'title': 'foobar',
                'slots': get_slots(0, len(fdata['slots'])),
            }, format='json')
            self.assertEqual(resp.status_code, 202)
            self.assertEqual(
                len(resp.data['slots']), len(fdata['slots']))

    def test_detail_patch_empty_slots(self):
        for n in fdata['events']:
            resp = self.client.patch(f'/{n}/', {'slots': []},
                format='json')
            self.assertEqual(resp.status_code, 202)
            self.assertEqual(len(resp.data['slots']), 0)

    def test_detail_patch_duplicate_slots_ignored(self):
        for n in fdata['events']:
            resp1 = self.client.get(f'/{n}/')
            slots = resp1.data['slots'] + resp1.data['slots']
            resp2 = self.client.patch(f'/{n}/', {'slots': slots},
                format='json')
            self.assertEqual(
                len(resp1.data['slots']), len(resp2.data['slots']))

    def test_detail_patch_parties_ignored(self):
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/')
        p_a = len(resp.data['parties'])
        
        # Add all parties, ignored
        resp = self.client.patch(f'/{n}/', {
            'parties': get_parties(0, len(fdata['emails'])),
            'slots': []
        }, format='json')
        resp = self.client.get(f'/{n}/')
        p_b = len(resp.data['parties'])
        self.assertEqual(p_a, p_b)

        # Clear parties, ignored
        resp = self.client.patch(f'/{n}/', {
            'parties': [],
            'slots': []
        }, format='json')
        resp = self.client.get(f'/{n}/')
        p_c = len(resp.data['parties'])
        self.assertEqual(p_a, p_c)

    @tag('todo')
    def test_detail_patch_fail(self):
        # todo
        n = fdata['events'][0]

        # Missing slots
        resp = self.client.patch(f'/{n}/', {'parties': []}, format='json')
        self.assertEqual(resp.status_code, 400)

        # Malformed slots - datetime
        resp = self.client.patch(f'/{n}/', {
            'slots': [{
                'begin': '2021-asdfT14:58:26.611000Z', 
                'duration': 'zy0:00:01'}]
        }, format='json')
        self.assertEqual(resp.status_code, 400)

        # Malformed slots - dict
        resp = self.client.patch(f'/{n}/', {'slots': {'bad': 'data'}},
            format='json')
        self.assertEqual(resp.status_code, 400)

        # Non-json format - strips slots/list with no error
        #   clearing slots has no effect
        resp = self.client.get(f'/{n}/')
        len_a = len(resp.data['slots'])
        resp = self.client.patch(f'/{n}/', {'slots': []})
        #self.assertEqual(resp.status_code, 400)
        resp = self.client.get(f'/{n}/')
        len_b = len(resp.data['slots'])
        self.assertEqual(len_a, len_b)

        # Non-json format, malformed slots - dict
        with self.assertRaises(AssertionError):
            resp = self.client.patch(f'/{n}/', {'slots': {'bad': 'data'}})

    def test_detail_delete(self):
        n = fdata['events'][0]
        resp = self.client.delete(f'/{n}/')
        self.assertEqual(resp.status_code, 204)



@tag('auth')
class ViewAuthTests(APITestCase):
    fixtures = fixture_files

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 

    def setUp(self):
        print(self._testMethodName)

    def loop_user_event_tests(self, method, path='', payload=None, 
        succ_code=200, fail_code=403):
        # Expect success for user in event or staff
        for uidx in range(len(fdata['users'])):
            uid = fdata['users'][uidx]
            uevts = fdata['uevents'][uidx]
            user = User.objects.get(pk=uid)
            self.client.force_login(user)
            for evt_id in fdata['events']:
                resp = eval('self.client.' + method)(f'/{evt_id}/{path}',
                    payload, format='json')
                is_staff = fdata['staff'][uidx]
                #if user.is_active and evt_id in uevts or user.is_staff:
                if user.is_active and evt_id in uevts or is_staff:
                    self.assertEqual(resp.status_code, succ_code)
                else:
                    self.assertEqual(resp.status_code, fail_code)

    @override_settings(DEBUG=True) # enable connection.queries
    @tag('todo', 'this')
    def test_service_enlog_fail(self):
        # todo
        #  test pg only
        # X: ServiceTests
        from schedul import services, models
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)
        evt_id = fdata['uevents'][0][0]
        user_id = fdata['users'][0]
        email = fdata['emails'][0]
        event = models.Event.objects.get(pk=evt_id)
        resp = self.client.get(f'/{evt_id}/')
        #st()
        services.enlog(event, email, 'UPDATE', gen_sched.gen_slots([32]))

        # todo
        from django.conf import settings
        print(settings.DATABASES['default']['ENGINE'])
        print(connection.vendor)
        #st()
        # X: mysql case (no strict mode)
        if 'mysql' in settings.DATABASES['default']['ENGINE']:
            with self.assertRaises(json.decoder.JSONDecodeError):
                resp = self.client.get(f'/{evt_id}/log/')

        #print(resp.data)
        #st()
        #self.assertTrue(False)


    def test_list_get_auth(self):
        for uidx in range(len(fdata['users'])):
            uid = fdata['users'][uidx]
            uevts = fdata['uevents'][uidx]
            user = User.objects.get(pk=uid)
            self.client.force_login(user)
            resp = self.client.get('/', format='json')
            is_staff = fdata['staff'][uidx]
            if user.is_active:
                if is_staff:
                    # All events
                    self.assertEqual(len(resp.data), len(fdata['events']))
                else:
                    # User events
                    self.assertEqual(len(resp.data), len(uevts))
            else:
                self.assertEqual(resp.status_code, 403)

    def test_list_post_auth(self):
        # Any active user can post
        for uidx in range(len(fdata['users'])):
            uid = fdata['users'][uidx]
            user = User.objects.get(pk=uid)
            self.client.force_login(user)
            payload = {
                'parties': get_parties(0, len(fdata['emails'])),
                'slots': get_slots(0, len(fdata['slots']))
            }
            resp = self.client.post('/', payload, format='json')
            if user.is_active: 
                self.assertEqual(resp.status_code, 201)
            else:
                self.assertEqual(resp.status_code, 403)


    def test_detail_get_auth(self):
        self.loop_user_event_tests('get')

    def test_detail_patch_auth(self):
        self.loop_user_event_tests('patch', '', {'slots': []}, 202, 403)

    @tag('todo-')
    def test_detail_delete_auth_fail(self):
        # todo- refactor a bit
        failu = []
        for eidx, eid in enumerate(fdata['events']):
            # Non-event-party non-staff active users
            u1 = [uu for u, uu in enumerate(fdata['users'])
                if uu not in fdata['eventp'][eidx]
                    and not fdata['staff'][u]
                    and fdata['active'][u]
            ]
            # Inactive users
            u2 = [uu for u, uu in enumerate(fdata['users'])
                if not fdata['active'][u]
            ]
            # In party, non-staff users
            u3 = [uu for u, uu in enumerate(fdata['users'])
                if uu in fdata['eventp'][eidx]
                    and not fdata['staff'][u]
            ]
            failu.append([u1, u2, u3])
        for idx, failers in enumerate(failu):
            evt_id = fdata['events'][idx]
            for uid in failers[0]:
                user = User.objects.get(pk=uid)
                #print(user.__dict__)
                self.client.force_login(user)
                resp = self.client.delete(f'/{evt_id}/')
                self.assertEqual(resp.status_code, 403)
            for uid in failers[1]:
                user = User.objects.get(pk=uid)
                #print(user.__dict__)
                self.client.force_login(user)
                resp = self.client.delete(f'/{evt_id}/')
                self.assertEqual(resp.status_code, 403)
            for uid in failers[2]:
                user = User.objects.get(pk=uid)
                #print(user.__dict__)
                #st()
                self.client.force_login(user)
                resp = self.client.delete(f'/{evt_id}/')
                self.assertEqual(resp.status_code, 403)


    def test_notify_post_auth(self):
        suser = User.objects.create(username='sup', is_staff=True)
        mail_count = 0
        for uidx in range(len(fdata['users'])):
            uid = fdata['users'][uidx]
            uevts = fdata['uevents'][uidx]
            user = User.objects.get(pk=uid)
            
            for evt_id in fdata['events']:
                evt_idx = fdata['events'].index(evt_id)
                ur_id = fdata['eventp'][evt_idx][0]
                ur_idx = fdata['users'].index(ur_id)
                u_eml = fdata['emails'][ur_idx]

                self.client.force_login(suser)
                resp = self.client.get(f'/{evt_id}/')

                self.client.force_login(user)
                resp = self.client.post(f'/{evt_id}/notify/', {'parties':
                    [u_eml], 'slots': resp.data['slots'], 'sender': u_eml},
                    format='json') 
                is_staff = fdata['staff'][uidx]

                if user.is_active and evt_id in uevts or is_staff:
                    mail_count += 1
                    self.assertEqual(resp.status_code, 202)
                else:
                    self.assertEqual(resp.status_code, 403)

                self.assertEqual(len(mail.outbox), mail_count)

    def test_log_get_auth(self):
        self.loop_user_event_tests('get', 'log/')

    
    ''' Emailtokens '''

    def test_list_get_emailtoken_fail(self):
        ue = 'nonesuch@localhost'
        evt_id, user, tok = setup_emailtoken(self, ue)
        resp = self.client.get(f'/?et={tok}')
        self.assertEqual(resp.status_code, 403)

    def test_list_post_emailtoken_fail(self):
        ue = 'nonesuch@localhost'
        evt_id, user, tok = setup_emailtoken(self, ue)
        resp = self.client.post(f'/?et={tok}', {
            'parties': get_parties(), 'slots': []})
        self.assertEqual(resp.status_code, 403)

    def test_detail_get_emailtoken(self):
        ur_eml = 'nonesuch@localhost'
        evt_id, user, tok = setup_emailtoken(self, ur_eml)
        resp = self.client.get(f'/{evt_id}/?et={tok}')
        self.assertEqual(resp.status_code, 200)

    @tag('todo-')
    def test_detail_get_emailtoken_fail(self):
        # todo- comments on strategy
        suser = User.objects.create(username='sup', is_staff=True)
        self.client.force_login(suser)

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

        user1 = User.objects.get(email=ur1_eml)
        user2 = User.objects.get(email=ur2_eml)
        tok1 = EmailToken.objects.get(user=user1, event_id=evt1_id).key
        tok2 = EmailToken.objects.get(user=user2, event_id=evt2_id).key
        # Token mismatches
        resp3 = self.client.get(f'/{evt2_id}/?et={tok1}')
        self.assertEqual(resp3.status_code, 403)
        resp4 = self.client.get(f'/{evt1_id}/?et={tok2}')
        self.assertEqual(resp4.status_code, 403)
    
    @tag('todo-')
    def test_detail_get_emailtoken_logviewed(self):
        # todo-
        ue = ur_eml = 'nonesuch@localhost'
        evt_id, usr, tok = setup_emailtoken(self, ue)
        log_a = fetch_log(self, evt_id)
        resp = self.client.get(f'/{evt_id}/?et={tok}')
        log_b = fetch_log(self, evt_id)
        self.assertEqual(len(log_a) + 1, len(log_b))
        self.assertEqual(log_b[-1]['occurrence'], 'VIEW')
        self.assertIn('token', log_b[-1]['data'])

    def test_detail_patch_emailtoken(self):
        ur_eml = 'nonesuch@localhost'
        evt_id, user, tok = setup_emailtoken(self, ur_eml)
        resp = self.client.patch(f'/{evt_id}/?et={tok}', {'slots': []},
            format='json')
        self.assertEqual(resp.status_code, 202)

    @tag('todo-')
    def test_detail_patch_emailtoken_fail(self):
        # todo-
        ue = 'nonesuch@localhost'
        tok_evt_id, tok_user, tok = setup_emailtoken(self, ue)
        nevt_id = fdata['events'][0]
        resp = self.client.patch(f'/{nevt_id}/?et={tok}', {'slots': []},
            format='json')
        self.assertEqual(resp.status_code, 403)

    @tag('todo-')
    def test_detail_patch_emailtoken_logupdate(self):
        # todo-
        evt_id = fdata['uevents'][0][0]
        user_id = fdata['users'][0]
        tok = EmailToken.objects.create(event_id=evt_id, user_id=user_id).key
        log_a = fetch_log(self, evt_id)
        resp = self.client.patch(f'/{evt_id}/?et={tok}', {'slots': []},
            format='json')
        log_b = fetch_log(self, evt_id)
        self.assertEqual(len(log_a) + 1, len(log_b))
        self.assertEqual(log_b[-1]['occurrence'], 'UPDATE')
        self.assertIn('token', log_b[-1]['data'])

    def test_notify_post_emailtoken(self):
        ue = 'nonesuch@localhost'
        tok_evt_id, tok_user, tok = setup_emailtoken(self, ue)

        resp_get = self.client.get(f'/{tok_evt_id}/?et={tok}')
        resp_noti = self.client.post(f'/{tok_evt_id}/notify/?et={tok}', 
            {'parties': [ue], 'slots': resp_get.data['slots'],
            'sender': ue}, format='json') 
        self.assertEqual(resp_noti.status_code, 202)

    def test_notify_post_emailtoken_fail(self):
        ue = 'nonesuch@localhost'
        tok_evt_id, tok_user, tok = setup_emailtoken(self, ue)

        resp_tok = self.client.get(f'/{tok_evt_id}/?et={tok}')

        # Anon user, no token
        resp_noti_t = self.client.post(f'/{tok_evt_id}/notify/', 
            {'parties': [ue], 'slots': resp_tok.data['slots'],
            'sender': ue}, format='json') 
        self.assertEqual(resp_noti_t.status_code, 403)
        
        nevt_id = fdata['events'][0]

        # Token/event mismatch
        resp_noti_n = self.client.post(f'/{nevt_id}/notify/?et={tok}',
            {'parties': [ue], 'slots': resp_tok.data['slots'],
            'sender': ue}, format='json') 
        self.assertEqual(resp_noti_n.status_code, 403)

    @tag('todo-')
    def test_notify_post_emailtoken_lognotify(self):
        # todo-
        ue = fdata['emails'][0]
        evt_id, user, tok = setup_emailtoken(self, ue)

        resp_get = self.client.get(f'/{evt_id}/?et={tok}')
        log_a = fetch_log(self, evt_id)
        len_a = len(log_a)

        resp_noti = self.client.post(f'/{evt_id}/notify/?et={tok}', 
            {'parties': [ue], 'slots': resp_get.data['slots'],
            'sender': ue}, format='json') 
        
        log_b = fetch_log(self, evt_id)
        self.assertEqual(len_a + 1, len(log_b))
        self.assertEqual(log_b[-1]['occurrence'], 'NOTIFY')
        self.assertIn('token', log_b[-1]['data'])


    @tag('todo-')
    def test_loggedinuser_emailtoken_ignored(self):
        # todo-
        # setup tok user 0, login user, get?tok, check log..
        evt_id = fdata['uevents'][0][0]
        user_id = fdata['users'][0]
        tok = EmailToken.objects.create(event_id=evt_id, user_id=user_id).key
        user = User.objects.get(pk=user_id)
        self.client.force_login(user)
        resp = self.client.get(f'/{evt_id}/?et={tok}')
        resp_log = self.client.get(f'/{evt_id}/log/')
        self.assertNotIn('token', resp_log.data['entries'][-1]['data'])
        
    @tag('todo')
    def test_loggedinuser_emailtoken_mismatch(self):
        # todo
        # in out  anon user staff  basic token
        #self.assertTrue(False)
        pass
    
    def test_log_get_emailtoken(self):
        ue = 'nonesuch@localhost'
        evt_id, usr, tok = setup_emailtoken(self, ue)
        resp = self.client.get(f'/{evt_id}/log/?et={tok}')
        self.assertEqual(resp.status_code, 200)

    def test_log_get_emailtoken_fail(self):
        user_id = fdata['users'][0]
        user = User.objects.get(pk=user_id)
        evt_id = fdata['uevents'][0][0]
        tok = EmailToken.objects.create(event_id=evt_id, user_id=user_id).key

        # X: implies fixture requrement
        evt_id = fdata['uevents'][0][1]
        resp = self.client.get(f'/{evt_id}/log/?et={tok}')
        self.assertEqual(resp.status_code, 403)

    @tag('todo-')
    def test_emailtoken_expired(self):
        # todo- double check this
        user_id = fdata['users'][0]
        user = User.objects.get(pk=user_id)
        evt_id = fdata['uevents'][0][0]
        tok = EmailToken.objects.create(
            event_id=evt_id, user_id=user_id, 
            expires=timezone.now() - timedelta(days=5)
            # X: relevant here?
            #expires=datetime.now() - timedelta(days=5)
        ).key
        resp = self.client.get(f'/{evt_id}/?et={tok}')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data[0].title(), 'Token Expired')



@tag('dispatch')
class DispatchViewTests(APITestCase):
    fixtures = fixture_files

    @classmethod
    def setUpClass(cls):
        super().setUpClass() 
        cls.suser = User.objects.create(username='sup', is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()

    def setUp(self):
        print(self._testMethodName)
        self.client.login(username='sup', password='p')


    def test_notify_get_fail(self):
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/notify/')
        self.assertEqual(resp.status_code, 405)

    def test_notify_post(self):
        evt_id = fdata['uevents'][0][0]
        user_id = fdata['users'][0]
        user = User.objects.get(pk=user_id)
        u_eml = user.email
        resp = self.client.get(f'/{evt_id}/')
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [u_eml],
            'slots': resp.data['slots'], 'sender': u_eml}, format='json') 
        self.assertEqual(resp.status_code, 202)
        self.assertEqual(len(mail.outbox), 1)

    #@tag('this')
    @tag('todo')
    def test_notify_post_fail(self):
        # todo
        users = []
        evt_ids = []
        user_ids = fdata['users']
        for uidx, uid in enumerate(user_ids):
            email = fdata['emails'][uidx]
            # X: ? use fixture - assumes covering pattern -- as above, coupling
            resp = self.client.post('/', {'parties': [email],
                'slots': get_slots(0, len(fdata['slots']))},
                format='json')
            evt_ids.append(resp.data['id'])
            evt_id = resp.data['id']
            slots = resp.data['slots']
            uidx_next = (uidx + 1) % len(user_ids)
            email_next = fdata['emails'][uidx_next]

            print(email_next)
            # X: excepting staff
            # Sender not in event
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                [email], 'slots': slots, 
                'sender': email_next},
                format='json')
            #self.assertEqual(resp.status_code, 400)

            # No such sender
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                [email], 'slots': slots, 
                'sender': 'nonesuch@localhost'},
                format='json')
            self.assertEqual(resp.status_code, 400)

            # Recipients not in event
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                [email_next, 'limbo@localhost'],
                'slots': slots, 'sender': 
                email}, format='json')
            self.assertEqual(resp.status_code, 400)
            
            # Slots mismatch
            slots.pop()
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                [email], 'slots': slots, 'sender': 
                email}, format='json')
            self.assertEqual(resp.status_code, 400)

            # No such slot
            slots = [dict(begin=str(timezone.now()), 
                duration=str(timedelta(hours=1)))]
            resp = self.client.post(f'/{evt_id}/notify/', {'parties': 
                [email], 'slots': slots, 'sender': 
                email}, format='json')
            self.assertEqual(resp.status_code, 400)


    def test_log_get(self):
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(resp.status_code, 200)

    def test_log_get_fail(self):
        n = len(fdata['events']) + 1
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(resp.status_code, 404)


    ''' Log entries '''

    def test_list_post_logupdate(self):
        resp = self.client.post('/', {
            'parties': get_parties(0, len(fdata['emails'])),
            'slots': get_slots(0, len(fdata['slots']))
        }, format='json')
        n = resp.data['id']
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(len(resp.data['entries']), 1)
        self.assertEqual(resp.data['entries'][-1]['occurrence'], 'UPDATE')

    def test_detail_get_logviewed(self):
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        resp = self.client.get(f'/{n}/')
        resp = self.client.get(f'/{n}/log/')
        len_b = len(resp.data['entries'])
        self.assertEqual(len_a + 1, len_b)
        self.assertEqual(resp.data['entries'][-1]['occurrence'], 'VIEW')

    @tag('todo-')
    def test_detail_get_logviewed_fail(self):
        # todo-
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        # Fail, redirect
        resp = self.client.get(f'/{n}')
        resp = self.client.get(f'/{n}/log/')
        len_b = len(resp.data['entries'])
        self.assertEqual(len_a, len_b)

    def test_detail_patch_logupdate(self):
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        resp = self.client.patch(f'/{n}/', {
            'slots': get_slots(0, len(fdata['slots']))
        }, format='json')
        resp = self.client.get(f'/{n}/log/')
        self.assertEqual(len(resp.data['entries']), len_a + 1)
        self.assertEqual(resp.data['entries'][-1]['occurrence'], 'UPDATE')

    @tag('this', 'todo-')
    def test_detail_patch_logupdate_fail(self):
        # todo-
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        # Fail, no payload
        resp = self.client.patch(f'/{n}/', format='json')
        resp = self.client.get(f'/{n}/log/')
        len_b = len(resp.data['entries'])
        self.assertEqual(len_a, len_b)

    def test_notify_post_lognotify(self):
        evt_id = fdata['uevents'][0][0]
        user_id = fdata['users'][0]
        user = User.objects.get(pk=user_id)
        u_eml = user.email
        resp_get = self.client.get(f'/{evt_id}/')

        resp = self.client.get(f'/{evt_id}/log/')
        len_a = len(resp.data['entries'])

        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [u_eml],
            'slots': resp_get.data['slots'], 'sender': u_eml}, format='json') 

        resp = self.client.get(f'/{evt_id}/log/')
        len_b = len(resp.data['entries'])
        self.assertEqual(len_a + 1, len_b)
        self.assertEqual(resp.data['entries'][-1]['occurrence'], 'NOTIFY')

    @tag('todo-')
    def test_notify_post_lognotify_fail(self):
        # todo-
        n = fdata['events'][0]
        resp = self.client.get(f'/{n}/log/')
        len_a = len(resp.data['entries'])
        # Fail, no payload
        resp = self.client.post(f'/{n}/notify/', format='json')
        resp = self.client.get(f'/{n}/log/')
        len_b = len(resp.data['entries'])
        self.assertEqual(len_a, len_b)


#@skip
@tag('queries')
@override_settings(DEBUG=True) # enable connection.queries
class ViewQueryTests(APITestCase):
    fixtures = fixture_files

    @classmethod
    def setUpTestData(cls):
        #st()
        print(len(connection.queries))
        cls.suser = User.objects.create(username='sup', is_staff=True)
        cls.suser.set_password('p')
        cls.suser.save()
        print(len(connection.queries))
        reset_queries()

    def setUp(self):
        print(self._testMethodName)
        self.client.login(username='sup', password='p')
        print(len(connection.queries))
        #expect = 16
        #self.assertEqual(len(connection.queries), expect)
        reset_queries()

        
    def test_list_get(self):
        expect = 9
        resp = self.client.get('/')
        #st()
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)

    def test_list_post(self):
        expect = 8
        resp = self.client.post('/', {'parties': get_parties(), 'slots': []},
            format='json')
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)
    
    def test_detail_get(self):
        expect = 7
        resp = self.client.get('/1/')
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)
    
    def test_detail_patch(self):
        expect = 11
        resp = self.client.patch('/1/', {'slots': []}, format='json')
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)
    
    #@skip
    def test_detail_delete(self):
        # X: varies on related ?
        expect = 12
        resp = self.client.delete('/1/')
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)
    
    def test_notify_post(self):
        #st()
        expect = 17
        expect = 21
        resp = self.client.post('/', {'parties': get_parties(), 'slots': []},
            format='json')
        evt_id = fdata['uevents'][0][0]
        user_id = fdata['users'][0]
        u_eml = fdata['emails'][0]
        resp = self.client.get(f'/{evt_id}/')
        print(len(connection.queries), resp.status_code)
        reset_queries()
        print(len(connection.queries), resp.status_code)
        resp = self.client.post(f'/{evt_id}/notify/', {'parties': [u_eml],
            'slots': resp.data['slots'], 'sender': u_eml}, format='json') 
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)
    
    #@skip
    def test_log_get(self):
        # X: varies on related
        expect = 6
        resp = self.client.get('/1/log/')
        print(len(connection.queries), resp.status_code)
        self.assertEqual(len(connection.queries), expect)

