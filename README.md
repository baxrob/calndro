
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)


## A toy appointment coordination API

under &#x1f477; &#x1f6a7; 128119 &#128679; 128736
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
    $$ cp config/eg.env config/.env \           #
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
you@thar:prompt$ HOST_PORT=8005 docker-compose up
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
%[tui]
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

%[testdo]
%[coverage]
```

### Architecture, design, process

```
<!-- this? -->
```

this that then though them thumb through thither thusly thou their thimble thistle thicket thunder the thinking threw
<img src="_m/IMG_1377-rot90-300-noexif.JPG" style="float: right;">

![initial sketch](_m/IMG_1377-rot90-300-noexif.JPG)

<img src="_m/IMG_1377-rot90-300-noexif.JPG" style="float: right;">

#### Tree

```
%[tree]
```

%[annotree]


#### Stats
```
%[cloc]

%[coverage]
```

### Next, possibly

```
- ghub tidy branch - 
- tests - 

- ssl, mailhog, gpg/pass
- dataclasses, 

- self-hosting, localnet day scheduling
```
<!-- X: ?
- ob@localhost $user example.com - fixture/gen
-->
