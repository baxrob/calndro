
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


# - Update with suitable selection - time slots can only be attenuated

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

