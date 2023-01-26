
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)


## An appointment coordination API

Contents: [scenario](#scenario) | [install](#install) | [api](#interface) | [tui](#tui) | [tests](#tests) | [design](#architecture-design-process) | [future](#next-possibly) | [ref](#ref)

---
<br>
<p align="center">
&mdash; <i>Document under &#128119; &#128679; &#128736;</i> &mdash;
</p>
<br>

This is a WIP POC. 
It's in an interim state with some cruft.
Briefly, its 
intent is similar to the core function of Calendly, or [cal.com](https://github.com/calcom/cal.com).

In summary:
> Invite registered or unregistered parties, narrow to agreement on a scheduled time span, send notification of updates, with all actions logged

```
propose -> narrow -> agree : audit
```
no ui

### Scenario

[ with [httpie](https://httpie.io), [jq](https://stedolan.github.io/jq/) ]

```
# You:


# - Instantiate a coordination proposal - note [tz..RFC]

evt_id=$(http -a $user:$pwd POST :8000/ \
    parties:='["you@here.net", "they@thar.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"},
             {"begin": "2022-11-01T01:11:22-02", "duration": "00:30"}]' \
    | jq .id)


# - Notify other parties

http -a $user:$pwd POST :8000/$evt_id/notify/ \
    parties:='["they@thar.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"},
             {"begin": "2022-11-01T01:11:22-02", "duration": "00:30"}]'



# They:


# - Receive message including link with temporary access token

http://$host:8000/$evt_id/?et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


# - View proposed event times

http GET :8000/$evt_id/ et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


# - Update with suitable selection - time slots can only be attenuated

http PATCH :8000/$evt_id/ \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


# - Notify other parties (note timezone shift and microsecond syntax)

http POST :8000/$evt_id/notify/ \
    parties:='["you@here.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.020000Z", "duration": "00:10"},
             {"begin": "2022-11-01T02:11:22+01:00", "duration": "00:20"}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7



# Later:


# - Interested parties can view logs of the process

http GET :8000/$evt_id/log/


# - and write clients to the API

http GET :8000/openapi

# - requesting and using a DRF Session auth token

http POST :8000/api-token-auth/ username=$user password=$pwd

#   {"token": "48fc19e55a884b24e77913542a9822917a9c167a"}   

http GET :8000 Authorization:'Token 48fc19e55a884b24e77913542a9822917a9c167a'

# - session auth is also enabled

```

### Install

#### Python Pip

[ with Python version >=3.8 ]



```
python3 -m venv venv \
    && . venv/bin/activate \
    && pip install -r requirements/base.txt \
    && cp config/eg.env config/.env \           #
    && scripts/reset.sh \                       #
    && ./manage.py runserver 0.0.0.0:8000
```

[note: ppa pyenv ..]

#### Docker

[ with [docker](https://docs.docker.com/get-docker/), [docker-compose](https://github.com/docker/compose) ]

```
Run:

docker-compose up

Or:

docker-compose -f compose-stage.yaml up

```

- The default [compose.yaml](compose.yaml) mounts the local sqlite db and runs Django's dev server
- The [compose-stage.yaml](compose-stage.yaml) config runs a posgresql service and gunicorn

_
- [pg, ngx]

```
./manage.py loaddata users schedul

#docker exec -it caldc ./manage.py loaddata users schedul

docker exec -it caldcs ./manage.py loaddata users schedul
```

ob zo ub : p

<!--
[up down logs exec / $file= $sys=ubu|alp %cmd[exec]]
-->

#### Envs

-
-
-
-



#### Fixtures

-
-
-
-


[1] See [schedul/fixtures/gen.py](schedul/fixtures/gen.py)


#### Admin




There is a full Django admin at
```$host/admin```

<img src="_m/admin_scaps/entries.png" width="250"> <img src="_m/admin_scaps/entries_1.png" width="250"> <img src="_m/admin_scaps/events.png" width="250"> <img src="_m/admin_scaps/events_1a.png" width="250"> <img src="_m/admin_scaps/events_1b.png" width="250"> <img src="_m/admin_scaps/events_1c.png" width="250">

### Interface

```
op        uri            methods
---------------------------------------------------------
list      /              get     post    
detail    /id/           get             patch     delete
notify    /id/notify             post
logs      /id/log        get
```

#### Auth
```
op        uri            method:auth*
---------------------------------------------------------
list      /              get:r*  post:r
detail    /id/           get:t           patch:t   delete:s
notify    /id/notify             post:t
logs      /id/log        get:r*

* t: unregistered event party with token; r: registered user, *party-to events; s: staff

```

#### OpenAPI

See [_m/openapi-schama.yaml](_m/openapi-schema.yaml)
or run
```./manage.py generateschema```
or visit $host/openapi

```
$path/ vs $path  dj/humyn vs api/machine
```

### TUI

See [scripts/tui.sh](scripts/tui.sh)

#### Example

<!-- X: %volatile -->
```
...
you@thar:prompt$ HOST_PORT=8005 docker-compose up
...
you@thar:prompt$ port=8005 scripts/tui.sh
config: ob p _ 8005 ob@localhost
  l   c   d[n]  p[n]  n[n]  g[n]  ?   q
> ?
l list events
c create - prompts for emails, time-spans
d[n] detail - view event number n
p[n] patch time-spans for event n
n[n] notify recipients for n
g[n] log - view dispatch/update logs
? help - this help
q quit
  l   c   d[n]  p[n]  n[n]  g[n]  ?   q
> d1
{
    "id": 1,
    "log_url": "http://localhost:8005/1/log/",
    "notify_url": "http://localhost:8005/1/notify/",
    "parties": [
        "ob@localhost",
        "zo@localhost"
    ],
    "slots": [
        {
            "begin": "2021-03-11T14:34:00Z",
            "duration": "00:58:00"
        },
        {
            "begin": "2021-03-16T09:53:00Z",
            "duration": "00:45:00"
        },
        {
            "begin": "2021-03-25T16:26:00Z",
            "duration": "00:40:00"
        }
    ],
    "title": "cybes",
    "url": "http://localhost:8005/1/"
}


  l   c   d[n]  p[n]  n[n]  g[n]  ?   q
> 

> c
create: enter party emails>
bobo@frofro.info
enter slots as YYYY-MM-DDThh:mm:ss[+-mm:ss/Z] hh:mm:ss, followed by blank>
2029-01-01T11:29 01:01
{
    "id": 4,
    "log_url": "http://localhost:8000/4/log/",
    "notify_url": "http://localhost:8000/4/notify/",
    "parties": [
        "bobo@frofro.info"
    ],
    "slots": [
        {
            "begin": "2029-01-01T11:29:00Z",
            "duration": "00:01:01"
        }
    ],
    "title": "pisaj",
    "url": "http://localhost:8000/4/"
}


  l   c   d[n]  p[n]  n[n]  g[n]  ?   q

> c

- awkward time entry .. rfc#..

```

<!--
```
%[??tuieg]
```
-->

### Tests

See [schedul/tests.py](schedul/test.py)

There are feature tests with branch coverage.
- I don't like the number of utility functions
- Some auth tests are excessive or redundant
- I need to stipulate assumptions built into the fixture structure

```
core axials ?
log authn/z pii disposabil

helper funcs .. pytest
integration / functional / feature: views, auth, dispatch, queries
..unit: token, mail

action : result : match condition
list_tests.sh

tooling : py dj drf
```

```
todos:
-----
test_detail_delete_auth_fail
test_detail_get_emailtoken_fail
test_detail_get_emailtoken_logviewed
test_detail_patch_emailtoken_fail
test_detail_patch_emailtoken_logupdate
test_notify_post_emailtoken_lognotify
test_loggedinuser_emailtoken_ignored
test_emailtoken_expired
test_detail_get_logviewed_fail
test_detail_patch_logupdate_fail
test_notify_post_lognotify_fail

mail tests
```

#### CI

basic
Python 3.8 - 3.10

env vars  above / gh

See [.github/workflows/ci.yml](.github/workflows/ci.yml)

https://github.com/nektos/act

#### Coverage
```
Name                     Stmts   Miss  Cover
--------------------------------------------
config/__init__.py           0      0   100%
config/asgi.py               4      4     0%
config/settings.py          44      0   100%
config/urls.py              11      2    82%
config/wsgi.py               4      4     0%
schedul/__init__.py          0      0   100%
schedul/admin.py            52      5    90%
schedul/apps.py              4      0   100%
schedul/models.py           51      6    88%
schedul/permissions.py       4      0   100%
schedul/serializers.py     123      0   100%
schedul/services.py         39      5    87%
schedul/tests.py           569      6    99%
schedul/urls.py              3      0   100%
schedul/views.py           129     27    79%
--------------------------------------------
TOTAL                     1037     59    94%

https://github.com/nedbat/coveragepy
```
<!--
https://coverage.readthedocs.io/en/6.3.2/
-->

### Architecture, design, process



```
....|....1....|....2....|....3....|....4....|....5....|....6....|....7....|....8....|....9....|....0
```

The core entity is the Event class
```
event
  parties   user | anon
  slots     [ begin, duration ]
  title     optional string
  log       [ entries ]
```
- Inclusion of non-registered emails creates inactive user records
- The list of time slots can only be narrowed once created
- A gibberish title is generated if one is not provided
- Creation, update, related notification, and deletion are logged in detail


```
            event                         
              parties >---< user
slot >------- slots           email 
  begin       title                          
  duration    log --------< entry           
                              when          
                              occurrence    
                              effector      
                              slots         
                              data
```
- user
- tz
- entry
- data  tok  opened/closed

#### Design
```
naming splay

disinterleaving
```

#### Security

```
- no incentive, eml/dt and evt title only
- disposability
- no disaster case
- PII cases, pwd reuse cases

core axials ?
log authn/z pii disposabil
```

#### Mail / messages

```
- sendmail, localnet
- _ mailhog
```
#### Time

...
```
RFC
RFC
```


#### Use cases
```
- storage, close/delete net, confirm, update flow
- confirm: view=  not req  updy same
- left to you cases

confirm : view vs update  all vs all-1

closed : slots [] or [1] + confirmation
delete reserved  only log of closing  future maint op

expected flow  reopen by copying title  prevserved in log  id is pk

```
#### Motivations
```
- no (g)ui  dj api  diag ver  test design  audit trail  containeren
- coherent (pythonic) subset of posix sh .. refiving
```
#### Process
```
layer
deriv
strategy
debug/diag / exper process

apifuz
lzydkr
act
grip

pdb / test loop
```



#### Stats

##### tree

```
.
├── compose
│   ├── hist_x23
│   ├── local
│   │   ├── dj.env
│   │   ├── Dockerfile
│   │   └── Dockerfile-alp-pg
│   └── stage
│       ├── dj.env
│       ├── Dockerfile-dj
│       ├── Dockerfile-pg
│       ├── entrypoint.sh
│       ├── ngx
│       │   ├── Dockerfile
│       │   └── nginx.conf
│       └── pg.env
├── compose-stage.yaml
├── compose.yaml
├── config
│   ├── asgi.py
│   ├── ci.env
│   ├── eg.env
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── schedul
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── scripts
    ├── init_pg.sh
    ├── list_tests.sh
    ├── reset.sh
    ├── stew.sh
    ├── stitch_readme.sh
    ├── tui.sh
    └── watch_readme.sh

```

##### cloc

```
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                          22            565            439           1844
Markdown                        10            334              0            893
JSON                             3              0              0            346
YAML                             5             10             19            326
Bourne Shell                     7             61             50            293
Dockerfile                       2              8             17             23
-------------------------------------------------------------------------------
SUM:                            49            978            525           3725
-------------------------------------------------------------------------------

https://github.com/AlDanial/cloc
```

##### wc
```
907	schedul/tests.py
228	schedul/views.py
175	schedul/serializers.py
158	schedul/fixtures/gen.py
101	schedul/models.py
83	schedul/admin.py
63	schedul/services.py
18	schedul/permissions.py
11	schedul/urls.py
6	schedul/apps.py
0	schedul/__init__.py
0	schedul/fixtures/__init__.py
```



<!--
....|....1....|....2....|....3....|....4....|....5....|....6....|....7....|....8....|....9....|....0
-->
<!--
#### A Story

<img src="_m/IMG_1377-rot90-300-noexif.JPG" align="right">

<pre align="left">

this that then though they thunk through 
thither thusly thar their tham
-
-
and
-
-
then
-
-
so
-
-


</pre>

<br clear="both">
-->
<!--
event
  parties
  slots
  title
  log
slot
  event
  begin
  duration
user
  events
entry
  when
  occurrence
  effector
  slots
  data


event                                               event                       
  parties   user | anon                               parties >---< user
  slots     [ begin, duration ]         slot >------- slots           events
  title     optional string               begin       title                     
  log       [ entries ]                   duration    log --------< entry       
                                                                      when      
                                                                      occurrence
                                                                      effector  
                                                                      slots     
                                                                      data      
     
-->

### Future considerations

```
- ghub tidy branch - 
- tests - finish, rework, pytest

- ssl 
- mailhog
- gpg/pass
- dataclasses, 

- self-hosting, localnet day scheduling

- ob@localhost $user example.com - fixture/gen

- cgit, grip

linting

m/tq db sms maint eml
beeptime / cron
celery redis kafka

caching
throttling
paging
gql flask fastapi
```

### Refs

- [Decoupled Django]() book
- [Django for APIs]() book
- [Django For Startups](https://alexkrupp.typepad.com/sensemaking/2021/06/django-for-startup-founders-a-better-software-architecture-for-saas-startups-and-consumer-apps.html) article by Alex Krupp 

```
pdfs _aux ../studi
py dj drf
```
---

<p align="center">
constructed with <a href="scripts/stitch_readme.sh">scripts/stitch_readme.sh</a>
</p>
