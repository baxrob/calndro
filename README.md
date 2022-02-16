<!--
![badge](https://github.com/baxrob/calndro/actions/workflows/ci.yml/badge.svg)
-->

```
A toy appointment coordination API


you:

http -a $user:$pwd POST :9000/ \
    parties:='["you@here.net", "they@thar.net", "them@whar.net"] \
    slots:='[{"begin": "", "duration": ""},
           '[{"begin": "", "duration": ""},
           '[{"begin": "", "duration": ""}]'


http -a $user:$pwd POST :9000/$evt_id/notify/ \
    parties:='["they@thar.net", "them@whar.net"] \
    slots:='[{"begin": "", "duration": ""},
           '[{"begin": "", "duration": ""},
           '[{"begin": "", "duration": ""}]'



they:

http://localhost:9000/$evt_id/?et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7

http GET :9000/$evt_id/ et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


http PATCH:9000/$evt_id/ \
    slots:='[{"begin": "", "duration": ""},
           '[{"begin": "", "duration": ""}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7


http POST :9000/$evt_id/notify/ \
    parties:='["you@here.net", "them@whar.net"] \
    slots:='[{"begin": "", "duration": ""},
           '[{"begin": "", "duration": ""}]' \
    et=1fe36bfa6f2f2567b5f7ea5a06e1e2202ad57ea7









```

