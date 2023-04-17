
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
Briefly, its 
intent is similar to the core function of Calendly, or [cal.com](https://github.com/calcom/cal.com).
It's in an interim state with some cruft
at the edges,
but the 
main structure and operation are
relatively settled. 
<!--
an unneccessary experiment toward assurability
-->

In summary:
> Invite registered or unregistered parties, narrow to agreement on a scheduled time span, send notification of updates, with <!--all--> actions logged

```
propose -> narrow -> agree : audit
```

There's no graphical interface, but a [tui](#tui). 
The
[api](#interface)
is
small, with [somewhat and in the direction of] minimal corners.
[Install](#install) with venv/pip or docker.
[Tests](#tests)
may
give a 
simplest 
overview.
Below, 
you
can/may/will
find
some elaboration on
[design](#architecture-design-process)
process,
including some [stats](#stats)
and [workflow](#process) notes,
possible [future](#next-possibly)
expansion/s
and some
[background/contributing] /
[referential](#ref)
material.

<!-- X: s/<blockquote><i> -->
```
Note: draft text is marked with '@draft' in <code> or <details> blocks below
```
<!--
 [or cli?]
, or comments 
```
> Conventions used in this document:\n\n
> \s\s some pre/code blocks connote provisional notes

\n


```
-->


First a scenario



<!--
[scenario](#scenario)

[scenario](#scenario)
[install](#install)
[api](#interface)
[tui](#tui)
[tests](#tests)
[design](#architecture-design-process)
[future](#next-possibly)
[ref](#ref)
-->

### Scenario



[ with [httpie](https://httpie.io), [jq](https://stedolan.github.io/jq/) ]

```
# You:


# - Instantiate a coordination proposal - with date-time strings per ISO 8601

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


# - Update with suitable selection

http PATCH :8000/$evt_id/ \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


# - Notify other parties (note microsecond syntax and timezone shift)

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

# - Session auth is also enabled

```

### Install

#### Python Pip

[ with Python version >=3.8 ]


To install and run in "one line"
```
python3 -m venv venv \
    && . venv/bin/activate \
    && pip install -r requirements/base.txt \
    && cp config/eg.env config/.env \           # @todo
    && scripts/reset.sh \                       # @todo
    && ./manage.py runserver 0.0.0.0:8000
```
<!--
[note: ppa pyenv .. https://github.com/pyenv/pyenv]
-->

#### Docker

[ with [docker](https://docs.docker.com/get-docker/), [docker-compose](https://github.com/docker/compose) ]

```
# Run:

docker-compose up

# Or:

docker-compose -f compose-stage.yaml up

# Pass a host port

HOST_PORT=8005 docker-compose up

```

- The default [compose.yaml](compose.yaml) creates or mounts the local db.sqlite3 and runs Django's dev server
- The [compose-stage.yaml](compose-stage.yaml) config runs a posgresql service and gunicorn


<!--
_
- [pg, ngx]
[up down logs exec / $file= $sys=ubu|alp %cmd[exec]]
```
```
-->


#### Fixtures

```
./manage.py loaddata users schedul

#docker exec -it caldc ./manage.py loaddata users schedul

docker exec -it caldcs ./manage.py loaddata users schedul
```
<!--
- minimal ?

ob zo ub : p
-->


See [schedul/fixtures/gen.py](schedul/fixtures/gen.py)


#### Envs

[config/eg.env](config/eg.env) contains a variable reference

```
@draft

dj environ
setting ENV_PATH
```

<!--

environ.Env.read_env(env.str(
    'ENV_PATH', 
    Path(__file__).resolve().parent / '.env'
))

-->
```
@draft
variable reference / defaults
__

DJANGO_SECRET_KEY

DJANGO_DEBUG

DJANGO_ADMINS
DJANGO_DEFAULT_FROM_EMAIL

STATIC_ROOT
ALLOWED_HOSTS

EMAILTOKEN_EXPIRATION_DAYS

DATABASE_ENGINE
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
DATABASE_HOST
DATABASE_PORT

EMAIL_SUBJECT_PREFIX='[calndro] '
EMAIL_USE_LOCALTIME=False
EMAIL_BACKEND=console filebased smtp locmem dummy 
EMAIL_FILE_PATH=/tmp/cald-mail

__

/cf : doc / use formats
#EMAIL_SUBJECT_PREFIX='[calndro] '
#EMAIL_USE_LOCALTIME=False
#EMAIL_BACKEND=console filebased smtp locmem dummy 
#EMAIL_FILE_PATH=/tmp/cald-mail

EMAIL_SUBJECT_PREFIX    #'[calndro] '
EMAIL_USE_LOCALTIME     #False
EMAIL_BACKEND=console   #filebased smtp locmem dummy 
EMAIL_FILE_PATH         #/tmp/cald-mail

#EMAIL_SUBJECT_PREFIX    #'[calndro] '
#EMAIL_USE_LOCALTIME     #False
#EMAIL_BACKEND=console   #filebased smtp locmem dummy 
#EMAIL_FILE_PATH         #/tmp/cald-mail

\cf

____

EMAIL_HOST
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_TIMEOUT
EMAIL_USE_TLS
EMAIL_USE_SSL
EMAIL_SSL_KEYFILE
EMAIL_SSL_CERTFILE

[%eg.env]
```
<!--
\cf [grip? ghub? breaks on single backslash in code/pre/tilde-triple]
-->


#### Admin

There is a full Django admin at
```$host/admin/```


<img src="_m/admin_scaps/entries.png" width="250"> <img src="_m/admin_scaps/entries_1.png" width="250"> <img src="_m/admin_scaps/events.png" width="250"> <img src="_m/admin_scaps/events_1a.png" width="250"> <img src="_m/admin_scaps/events_1b.png" width="250"> <img src="_m/admin_scaps/events_1c.png" width="250">

<!-- ugh
<span style="display: inline-block;" align="center"><span style="display: block;">entries</span><img src="_m/admin_scaps/entries.png" width="250"></span> <img src="_m/admin_scaps/entries_1.png" width="250"> <img src="_m/admin_scaps/events.png" width="250"> <img src="_m/admin_scaps/events_1a.png" width="250"> <img src="_m/admin_scaps/events_1b.png" width="250"> <img src="_m/admin_scaps/events_1c.png" width="250">
-->

<br>

### Interface

There are four endpoints with seven supported method calls altogether
```
op        uri            methods
---------------------------------------------------------
list      /              get     post    
detail    /id/           get             patch     delete
notify    /id/notify             post
logs      /id/log        get
```

#### Auth

Access varies by three user classes - staff, registered, and temporary token access
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
or visit ```$host/openapi```

```
@draft

$path/ vs $path  dj/humyn vs api/machine
```

### TUI

See [scripts/tui.sh](scripts/tui.sh) 

``` @todo: notify/sender```

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
enter slots as YYYY-MM-DDThh[:mm:ss+-hh:mm/Z] hh[:mm:ss], followed by blank>
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

>

```
<!--

- awkward time entry .. rfc#..
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


<details>
<summary>@draft</summary>

```
overly parameterized

core axials ?
log authn/z pii disposabil

helper funcs .. pytest
integration / functional / feature: views, auth, dispatch, queries
..unit: token, mail

action : result : match condition
stitching together axiomatic view
thinking toward
formal verification
nice of self-doc typed api tools

list_tests.sh

tooling : py dj drf
```
</details>

```
todos:
-----
verify:
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

finish:
test_list_post_fail
test_detail_patch_title_change
test_detail_patch_fail
test_service_enlog_fail
test_loggedinuser_emailtoken_mismatch

add:
mail tests
env tests
docker tests
tui tests

refactor:
fixture axiomatics
pytest
```

#### CI

Basic github workflow running Python 3.8 - 3.10. See [.github/workflows/ci.yml](.github/workflows/ci.yml)

Using ```Act``` frequently, an offline github workflow runner: https://github.com/nektos/act

#### Coverage
```
Name                     Stmts   Miss  Cover
--------------------------------------------
config/__init__.py           0      0   100%
config/asgi.py               4      4     0%
config/settings.py          45      0   100%
config/urls.py               9      2    78%
config/wsgi.py               4      4     0%
schedul/__init__.py          0      0   100%
schedul/admin.py            52      5    90%
schedul/apps.py              4      0   100%
schedul/models.py           57      1    98%
schedul/permissions.py       6      0   100%
schedul/serializers.py     122      0   100%
schedul/services.py         39      1    97%
schedul/tests.py           597      6    99%
schedul/urls.py              3      0   100%
schedul/views.py            88      0   100%
--------------------------------------------
TOTAL                     1030     23    98%

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
- Inclusion of non-registered email creates an inactive user record
- Party/user list cannot be altered after event creation
- Time slot list can be narrowed or extended indefinitely
- A gibberish title is generated if one is not provided
- Creation, update, related notification, and deletion are logged in detail


An Event has three main relations, to user/parties, time slots, and log entries
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
- ```User``` is a relation to Django/AUTH_USER_MODEL, relying only on email address
- The ```begin``` field of a ```slot``` is a normal timezone-aware Django db field
- Log ```entry``` is a flat structure[, so there are no second order relations]
- The ```slots``` field of a log ```entry``` is thus fixed size, which places a limit on the number of slots
- The ```data``` field of a log ```entry``` stores indication of token usage, notification recipient, and/or event open/close actions as applicable


An EmailToken is created and sent with notifications for non-authenticated access
```
emailtoken
  event >--- event
  user >---- user
  key
  expires
```
Expiration defaults to five days, or the value of EMAILTOKEN_EXPIRATION_DAYS setting


#### Design

<details>
<summary>@draft</summary>

```
disinterleaving
naming splay  splay:join
complexities  auth  tok  log
awareness enhancing  design  practice  strategem

axials:
fixed parties : avoid confusion : log clarity ; reset op: copy slots title, close

```
```
career: 
...
```

</details>

##### Cases

<details>
<summary>@draft</summary>

```
groupings:
- storage, close/delete net, confirm, update flow
- left to you cases - realistically, overlays on spec

closed : slots [] or [1] + confirmation
delete reserved  only log of closing  future maint op

confirm: view=  not req  updy same
confirm : view vs update  all vs all-1

expected flow  reopen by copying title  prevserved in log  id is pk

- ewe eye  mechane
- lamport/vector test
- beeptime net
- machine <-> machine

aspects:
soa dj drf  eval study integrate
net time
sec contain
wrkflow tooling

```

- 

</details>


##### Security

The project aims to be small, coherent, and auditable.

<details>
<summary>@draft</summary>

```
- no incentive, eml/dt and evt title only
- disposability
- no disaster case
- PII cases, pwd reuse cases

core axials ?
log authn/z pii disposabil

..roles?
sender initiator
recipient token
staff super
[mailhost]
```
</details>

##### Mail / notifications

```
@draft

- sendmail, localnet
- _ mailhog

agnostic on agree/confirm operation process
mail  sms  talk
m/t q
myriad svc net
celery redis kafka  broker queue


req slots to match latest
  no mis-notification
   ?error means
```

##### Time


<details>
<summary>@draft</summary>

```
ISO 8601
RFC 3339
https://stackoverflow.com/questions/522251/whats-the-difference-between-iso-8601-and-rfc-3339-date-formats
[RFC 2822]

CSP papers 1,2,3  hickey
```

</details>


##### Validation

```
@draft

post
patch
notify
delete
```
<!--
list      /              get     post    
detail    /id/           get             patch     delete
notify    /id/notify             post
logs      /id/log        get
-->

##### Logs

```
@draft

event
parties
entries
  id
  when
  occurrence : update | notify | view
  effector : user
  slots
  data : { token, opened, closed, recipient }
```

##### Documentation

- Using ```Grip``` to draft and review this file outside github: https://github.com/joeyespo/grip
- @todo: docstrings

<!-- @draft
break:
- comments in backbackbackticks
- see env section comment

.. wait, breaking via script/mine or gh.md ?
-->

``` &lt; \n ```

<!-- @draft
##### Extensibility
-
-
-->

##### Motivations

<details>
<summary>@draft</summary>

```
minima complexity

career / tech path

- no (g)ui  dj api  diag ver  test design  audit trail  containeren
- coherent (pythonic) subset of posix sh .. refining
small scale code/arch/test/etc view tools
sh -> py underview
    py wraps unix/posix

network experiments
```

</details>


#### Process

<details>
<summary>@draft</summary>

```
gluing together
sense of flow
layer
deriv
strategy
debug/diag / exper process
  work loop
pdb / test loop
    reinventing sh

act
lzydkr
grip
apifuz

```

</details>



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
Python                          18            490            227           1794
Markdown                        10            520              0           1390
JSON                             3              0              0            349
YAML                             5             10             18            326
Bourne Shell                     7             62             50            302
Dockerfile                       2              8             17             23
-------------------------------------------------------------------------------
SUM:                            45           1090            312           4184
-------------------------------------------------------------------------------

https://github.com/AlDanial/cloc
```

##### wc
```
969	schedul/tests.py
180	schedul/serializers.py
135	schedul/views.py
111	schedul/fixtures/gen.py
84	schedul/models.py
82	schedul/admin.py
60	schedul/services.py
14	schedul/permissions.py
11	schedul/urls.py
6	schedul/apps.py
0	schedul/__init__.py
0	schedul/fixtures/__init__.py
```

### Future considerations

```
@draft

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
@draft

pdfs _aux ../studi
py dj drf
```
---

<p align="center">
constructed with <a href="scripts/stitch_readme.sh">scripts/stitch_readme.sh</a>
</p>
