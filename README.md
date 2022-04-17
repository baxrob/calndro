
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)


## A toy appointment coordination API

Contents: [scenario](#scenario) | [install](#install) | [tui](#tui) [api](#interface) | [tests](#tests) | [design](#architecture-design-process) | [future](#next-possibly) | [ref](#ref)

---

Document under &#x1f477; &#x1f6a7; 128119 &#128679; 128736
_ _
👷🚧🛠
```
_ _
👷
under &#x1f477;
```
<!-- [cruft/schlock note] -->

### Scenario

[ with [httpie](https://httpie.io), [jq](https://stedolan.github.io/jq/) ]

```
you:


- instantiate a coordination proposal

evt_id=$(http -a $user:$pwd POST :8000/ \
    parties:='["you@here.net", "they@thar.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"},
             {"begin": "2022-11-01T01:11:22-02", "duration": "00:30"}]' \
    | jq .id)


- notify other parties

http -a $user:$pwd POST :8000/$evt_id/notify/ \
    parties:='["they@thar.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"},
             {"begin": "2022-11-01T01:11:22-02", "duration": "00:30"}]'



they:


- receive message including link with temporary access token

http://$host:8000/$evt_id/?et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


- view proposed event times

http GET :8000/$evt_id/ et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


- update with suitable selection

http PATCH :8000/$evt_id/ \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


- notify other parties

http POST :8000/$evt_id/notify/ \
    parties:='["you@here.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.020000Z", "duration": "00:10"},
             {"begin": "2022-11-01T02:11:22+01:00", "duration": "00:20"}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7



later:


- everyone can enjoy logs of the process

http GET :8000/$evt_id/log/


- and gaze at the API

http GET :8000/openapi
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
<!--
[up down logs exec / $file= $sys=ubu|alp %cmd[exec]]
-->

#### Envs, fixtures, admin


```
./manage.py loaddata users schedul

#docker exec -it caldc ./manage.py loaddata users schedul

docker exec -it caldcs ./manage.py loaddata users schedul
```
[1] See [gen.py](schedul/fixtures/gen.py)

[2] [$host/admin .. ..]

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
c create with emails, time-spans
d[n] detail - view event number n
p[n] patch time-spans
n[n] notify recipients
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

```
```
%[??tuieg]
```

### Interface

See [openapi-schama.yaml](_m/openapi-schema.yaml)

```
```

### Tests

See [tests.py](schedul/test.py)

```
helper funcs .. pytest
integration: views, auth, dispatch, ..queries
..unit: token, mail
```

```
todos:
-----
97-    def test_detail_patch_dupe(self):
98:        # todo-
--
264-    def test_detail_delete_auth_fail(self):
265:        # todo-
--
336-    def test_notify_post_auth_fail(self):
337:        # todo-
--
439-    def test_detail_get_emailtoken_fail(self):
440:        # todo-
--
476-    def test_detail_patch_emailtoken(self):
477:        # todo-
--
499-    def test_detail_patch_emailtoken_fail(self):
500:        # todo-
--
512-    def test_notify_post_emailtoken(self):
513:        # todo
--
516-    def test_notify_post_emailtoken_fail(self):
517:        # todo
--
524-    def test_emailtoken_expired(self):
525:        # todo
--
578-    def test_notify_post(self):
579:        # todo-
--
599-    def test_notify_post_fail(self):
600:        # todo-
--
649-    def test_notify_post_lognotify(self):
650:        # todo-
--
673-    def test_detail_get_emailtoken_logviewed(self):
674:        # todo

```

### Architecture, design, process

```
<!-- this? -->
```

<img src="_m/IMG_1377-rot90-300-noexif.JPG" align="right">
<pre align="left">
this that then though they thunk through thither thusly thar their tham
this that then though they thunk through thither thusly thar their tham
</pre>
<br clear="both">

<!--
![initial sketch](_m/IMG_1377-rot90-300-noexif.JPG)
-->

#### Tree

```
.
├── compose
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
├── docker-compose.png
├── LICENSE
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
    ├── chore.sh
    ├── init_pg.sh
    ├── init.sql
    ├── reset.sh
    ├── stitch_readme_0.sh
    ├── stitch_readme.sh
    └── tui.sh

7 directories, 39 files
```

%[..annotree]


#### Stats
```
cloc[1]:

Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                          22            517            483           1671
JSON                             3              0              0            346
Markdown                         1             93              0            337
YAML                             5             10             18            326
Bourne Shell                     7             59             39            274
Dockerfile                       2              8             17             23
-------------------------------------------------------------------------------
SUM:                            40            687            557           2977
-------------------------------------------------------------------------------


wc:

212 schedul/views.py
158 schedul/fixtures/gen.py
83 schedul/admin.py
6 schedul/apps.py
100 schedul/models.py
175 schedul/serializers.py
16 schedul/permissions.py
0 schedul/__init__.py
57 schedul/services.py
11 schedul/urls.py
755 schedul/tests.py


coverage[2]:

%[nocoverage]
```
[1] https://github.com/AlDanial/cloc

[2] https://coverage.readthedocs.io/en/6.3.2/

### Next, possibly

```
- ghub tidy branch - 
- tests - finish, rework, pytest

- ssl, mailhog, gpg/pass
- dataclasses, 

- self-hosting, localnet day scheduling

- ob@localhost $user example.com - fixture/gen
```

### Refs

- 

---

<p align="center">
constructed with <a href="scripts/stitch_readme.sh">stitch_readme.sh</a>
</p>
