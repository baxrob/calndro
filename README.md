
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)

```
# A toy appointment coordination API


## Scenario



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

http://localhost:8000/$evt_id/?et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


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
    slots:='[{"begin": "2022-11-01T01:11:22.020000Z", "duration": ""},
             {"begin": "2022-11-01T02:11:22+01:00", "duration": ""}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7



later:


- everyone can enjoy logs of the process

http GET :8000/$evt_id/log/


- and gaze at the API

http GET :8000/openapi
```

