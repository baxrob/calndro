'''
< schedul.json jq '.[]|select(.model == schedul.timespan).fields|{begin,duration}'

{
  "begin": "2021-12-24T22:58:26.611000Z",
  "duration": "02:30:00"
}
{
  "begin": "2021-12-24T21:58:26.611000Z",
  "duration": "02:30:00"
}
{
  "begin": "2021-12-24T23:58:26.611000Z",
  "duration": "01:30:00"
}
{
  "begin": "2021-12-27T22:58:26.611000Z",
  "duration": "00:30:00"
}
{
  "begin": "2021-12-26T20:58:26.611000Z",
  "duration": "02:00:00"
}
{
  "begin": "2021-12-28T12:58:26.611000Z",
  "duration": "02:10:00"
}
{
  "begin": "2021-12-28T14:58:26.611000Z",
  "duration": "00:33:45"
}
'''
import datetime
import zoneinfo
import calendar
import random
#from ipdb import set_trace as st
from pdb import set_trace as st
import json

from calendar import monthrange
from random import choice, randrange
from datetime import datetime as dt
from zoneinfo import ZoneInfo
#from django.utils import timezone


datetime.datetime.strptime('2012-12-30 19:00 +0100', "%Y-%m-%d %H:%M %z")
ddd=datetime.datetime.strptime('2012-12-30 19:00 +0100', "%Y-%m-%d %H:%M %z")
ddd
ddd.isocalendar()
ddd.isoformat()

dt = datetime.datetime(2020, 10, 31, 12, tzinfo=zoneinfo.ZoneInfo("America/Los_Angeles"))
#dt_utc = datetime.datetime(2020, 11, 1, 8, tzinfo=timezone.utc)
LOS_ANGELES = zoneinfo.ZoneInfo("America/Los_Angeles")
#print((dt_utc + datetime.timedelta(hours=1)).astimezone(LOS_ANGELES))

dbg = True

dt_fmt = '%Y-%m-%dT%H:%M:%S.%f%z'

def gen_span(year, mrng, drng, hrng, nrng=[0, 59], srng=[0], msrng=[0]):
    dur = random.randint(10, 90)
    dbg and print(vars())
    m = mrng[0] if len(mrng) == 1 else random.randint(*mrng)
    d = drng[0] if len(drng) == 1 else random.randint(*drng)
    h = hrng[0] if len(hrng) == 1 else random.randint(*hrng)
    n = nrng[0] if len(nrng) == 1 else random.randint(*nrng)
    s = srng[0] if len(srng) == 1 else random.randint(*srng)
    ms = msrng[0] if len(msrng) == 1 else random.randint(*msrng)
    #begin = datetime.datetime(year, m, d, h, n, s, ms, tzinfo=timezone.utc)
    #begin = datetime.datetime(year, m, d, h, n, s, ms, timezone.utc)
    begin = datetime.datetime(year, m, d, h, n, s, ms, zoneinfo.ZoneInfo('UTC'))
    duration = datetime.timedelta(minutes=dur)
    fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
    #return dict(begin=begin, duration=duration) 
    return dict(begin=begin.strftime(fmt), duration=str(duration)) 
    #return dict(begin=str(begin), duration=str(duration)) 
    

def gen_spans(crng=[3]):
    c = crng[0] if len(crng) == 1 else random.randint(*crng)
    dbg and print(c)
    spandata = []
    today = datetime.date.today()
    year = random.choice([-1, 0, 1]) + today.year
    month = random.choice(range(12)) + 1
    for i in range(c):
        mlast = calendar.monthrange(year, month)[1]
        sdom = random.choice(range(mlast)) + 1
        dbg and print(sdom, mlast)
        edom = random.choice(range(sdom, mlast + 1))
        spandata.append(gen_span(year, [month], [sdom, edom], [9, 17]))
    return spandata

'''
bb = {
    "begin": "2021-01-17T13:54:00.000000+0000",
    "duration": "0:11:00"
}
fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
begin = datetime.strptime(bb['begin'], fmt)
dur = datetime.strptime(bb['duration'], '%H:%M:%S')
duration = timedelta(hours=dur.hour, minutes=dur.minute, seconds=dur.second)
'''
def obj_span(span):
    begin_fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
    dur_dt = datetime.datetime.strptime(span['duration'], '%H:%M:%S')
    return {
        'begin': datetime.datetime.strptime(span['begin'], begin_fmt),
        'duration': datetime.timedelta(hours=dur_dt.hour, minutes=dur_dt.minute,
            seconds=dur_dt.second)
    }

def gen_fixtures(evt_users=[[1,2],[1,3],[2,3]], evt_slots=[3,4,5]):
    # X:
    usr_eml = ['ob@localhost', 'zo@localhost', 'ub@localhost']
    span_count = 0
    fixt = []
    for idx, uu in enumerate(evt_users):
        evt_id = idx + 1;
        dt_now = datetime.datetime.now(zoneinfo.ZoneInfo('UTC')).strftime(dt_fmt)
        evt_item = {'model': 'schedul.event', 'pk': evt_id,
            'fields': {'parties': uu}}
        slots = gen_spans([evt_slots[idx]])
        span_items = []
        for jdx in range(evt_slots[idx]):
            slot_item = {'model': 'schedul.timespan', 'fields': {'event': evt_id}}
            slot_item['pk'] = jdx + span_count + 1
            slot_item['fields'].update(slots[jdx])
            span_items.append(slot_item)
        span_count += jdx + 1
        json_slots = json.dumps(slots)
        dlog_item = {'model': 'schedul.dispatchlogentry', 'pk': evt_id,
            'fields': {'event': evt_id, 'when': dt_now, 'occurrence': 'UPDATE',
                'effector': usr_eml[uu[0]], 'slots': json_slots}}
        fixt.extend([evt_item, dlog_item, *span_items])
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
        #arg = [int(sys.argv[1])] if len(sys.argv) > 1 else [3]
        for i in range(1, arglen):
            s = gen_spans([int(sys.argv[i])])
            print(json.dumps(s))
    else:
        s = gen_spans()
        print(json.dumps(s))
