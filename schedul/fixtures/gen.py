#! /usr/bin/env python3

'''
An crufty inconvenient fixture generator interface
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

from calendar import monthrange
from random import choice, randrange
from datetime import datetime as dt

import os
dbg = os.environ.get('GEN_DBG', False)

# X: config? how? ? break out tests/ package, or submodule in schedul ?
usr_eml = ['ob@localhost', 'zo@localhost', 'ub@localhost']

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

def gen_fixtures(evt_users=[[1,2],[1,3],[2,3]], evt_slots=[3,4,5]):
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
        dlog_item = {'model': 'schedul.dispatchlogentry', 'pk': evt_id,
            'fields': {'event': evt_id, 'when': dt_now, 'occurrence': 'UPDATE',
                'effector': usr_eml[uu[0]], 'slots': json_slots,
                'data': {'opened': 'created'}}}
        fixt.extend([evt_item, dlog_item, *slot_items])
    return fixt

def print_fixtures():
    print(json.dumps(gen_fixtures(), indent=4))

if __name__ == '__main__':
    import sys
    dbg = False
    arglen = len(sys.argv)
    if arglen > 1:
        if sys.argv[1] == 'fixt':
            print_fixtures()
            exit()
        for i in range(1, arglen):
            s = gen_slots([int(sys.argv[i])])
            print(json.dumps(s))
    else:
        s = gen_slots()
        print(json.dumps(s))

