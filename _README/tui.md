
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
%[tuieg]
```
-->
