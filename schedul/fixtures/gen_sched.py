#!/usr/bin/env python3

'''
A crufty inconvenient fixture generator interface

# Print sets of timespans
# 
gen_sched.py [count1 count2 ...]

# Print local dev fixtures - fixed set
# fixtures include event/s, timespan, and dispatchlogentries of creation
# ..effector
gen_sched.py fixt

# Print schedul fixtures for emails, in combinations of subsequence-count
# gen_sched.py a@b c@d e@f g@h 2 3 4
# - prints all two-party, three-party, and four-party sub-permutations of emails
gen_sched.py email [email ...] subsequence-count [subseq-count ...]


# Tests
./gen_sched.py a@b c@d e@f g@h 2 3 4  | less
./gen_sched.py fixt  | less
./gen_sched.py 6 9 5  | less

'''

import datetime
import calendar
import random
import json

from sys import version_info
if version_info.minor < 9:
    from backports import zoneinfo
else:
    import zoneinfo

#from calendar import monthrange
#from datetime import datetime as dt
from itertools import combinations
from random import choice

import os
dbg = os.environ.get('GEN_DBG', False)

dev_eml = ['ob@localhost', 'zo@localhost', 'ub@localhost']

dt_fmt = '%Y-%m-%dT%H:%M:%S.%f%z'

def gen_slot(year, mrng, drng, hrng, nrng=[0, 59], srng=[0], msrng=[0]):
    dur = random.randint(10, 90)
    dbg and print(vars())
    m = mrng[0] if len(mrng) == 1 else random.randint(*mrng)
    d = drng[0] if len(drng) == 1 else random.randint(*drng)
    h = hrng[0] if len(hrng) == 1 else random.randint(*hrng)
    n = nrng[0] if len(nrng) == 1 else random.randint(*nrng)
    s = srng[0] if len(srng) == 1 else random.randint(*srng)
    ms = msrng[0] if len(msrng) == 1 else random.randint(*msrng)
    begin = datetime.datetime(year, m, d, h, n, s, ms, zoneinfo.ZoneInfo('UTC'))
    duration = datetime.timedelta(minutes=dur)
    fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
    return dict(begin=begin.strftime(fmt), duration=str(duration)) 
    

def gen_slots(crng=[3]):
    c = crng[0] if len(crng) == 1 else random.randint(*crng)
    dbg and print(c)
    slotdata = []
    today = datetime.date.today()
    year = random.choice([-1, 0, 1]) + today.year
    month = random.choice(range(12)) + 1
    for i in range(c):
        mlast = calendar.monthrange(year, month)[1]
        sdom = random.choice(range(mlast)) + 1
        dbg and print(sdom, mlast)
        edom = random.choice(range(sdom, mlast + 1))
        slotdata.append(gen_slot(year, [month], [sdom, edom], [9, 17]))
    return slotdata

def obj_slot(slot):
    begin_fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
    dur_dt = datetime.datetime.strptime(slot['duration'], '%H:%M:%S')
    return {
        'begin': datetime.datetime.strptime(slot['begin'], begin_fmt),
        'duration': datetime.timedelta(hours=dur_dt.hour,
            minutes=dur_dt.minute, seconds=dur_dt.second)
    }

def gen_fixtures(evt_users=[[1,2],[1,3],[2,3]], evt_slots=[3,4,5], 
    usr_eml=None):
    slot_count = 0
    fixt = []
    for idx, uu in enumerate(evt_users):
        evt_id = idx + 1;
        dt_now = datetime.datetime.now(
            zoneinfo.ZoneInfo('UTC')).strftime(dt_fmt)
        evt_item = {'model': 'schedul.event', 'pk': evt_id,
            'fields': {'parties': uu}}
        slots = gen_slots([evt_slots[idx]])
        slot_items = []
        for jdx in range(evt_slots[idx]):
            slot_item = {'model': 'schedul.timespan',
                'fields': {'event': evt_id}}
            slot_item['pk'] = jdx + slot_count + 1
            slot_item['fields'].update(slots[jdx])
            slot_items.append(slot_item)
        slot_count += jdx + 1
        json_slots = json.dumps(slots)
        #print(uu, usr_eml)
        dlog_item = {'model': 'schedul.dispatchlogentry', 'pk': evt_id,
            'fields': {'event': evt_id, 'when': dt_now, 'occurrence': 'UPDATE',
                'effector': usr_eml[uu[0] - 1], 'slots': json_slots,
                'data': {'opened': 'created'}}}
        fixt.extend([evt_item, dlog_item, *slot_items])
    return fixt


if __name__ == '__main__':
    import sys
    dbg = False
    arglen = len(sys.argv)
    if arglen > 1:
        if sys.argv[1] == 'fixt':
            print(json.dumps(gen_fixtures(usr_eml=dev_eml), indent=4))
        elif not sys.argv[1].isdigit():
            idx = 1
            emails = []
            nums = []
            while idx < len(sys.argv) and not sys.argv[idx].isdigit():
                emails.append(sys.argv[idx])
                idx += 1
            while idx < len(sys.argv):
                nums.append(int(sys.argv[idx]))
                idx += 1

            usr_count = len(emails)
            usr_ids = range(1, usr_count + 1)
            nums = list(usr_ids) if len(nums) == 0 else nums
            evt_users = []
            for n in nums:
                evt_users.extend(combinations(usr_ids, n))
            evt_slots = [3] * len(evt_users)
            dbg and print(emails, evt_users, list(evt_slots))
            print(json.dumps(gen_fixtures(evt_users, evt_slots, emails)))
        else:
            for i in range(1, arglen):
                s = gen_slots([int(sys.argv[i])])
                print(json.dumps(s))
    else:
        s = gen_slots()
        print(json.dumps(s))

