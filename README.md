
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)

```


# A toy appointment coordination API


## Scenario


you:


- instantiate a coordination proposal

evt_id=$(http -a $user:$pwd POST :9000/ \
    parties:='["you@here.net", "they@thar.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"},
             {"begin": "2022-11-01T01:11:22-02", "duration": "00:30"}]' \
    | jq .id)


- notify other parties

http -a $user:$pwd POST :9000/$evt_id/notify/ \
    parties:='["they@thar.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"},
             {"begin": "2022-11-01T01:11:22-02", "duration": "00:30"}]'


they:


- receive message including link with temporary access token

http://localhost:9000/$evt_id/?et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


- view proposed event times

http GET :9000/$evt_id/ et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


- update with suitable selection

http PATCH :9000/$evt_id/ \
    slots:='[{"begin": "2022-11-01T01:11:22.02", "duration": "00:10"},
             {"begin": "2022-11-01T01:11:22+02", "duration": "00:20"}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


- notify other parties

http POST :9000/$evt_id/notify/ \
    parties:='["you@here.net", "them@whar.net"]' \
    slots:='[{"begin": "2022-11-01T01:11:22.020000Z", "duration": ""},
             {"begin": "2022-11-01T02:11:22+01:00", "duration": ""}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7



later:

- everyone views logs of the process

http GET :9000/$evt_id/log/


- and gazes at the API

http GET :9000/openapi



[see: jq, httpie]


### Previously


- run in container

[docker.sh:


- or like a normal Django project
  - copy config/.env.ci to config/.env and edit per yer cetera
  - see Dockerfile or .github/workflows/ci.yml for eg
  - and/or use `pip install -r requirements/test.txt` to get httpie if not installed
  - and/or use `python manage.py testserver users schedul --addrport=0.0.0.0:9999`
rather than runserver


## Meanwhile

- why?

[...]




```

