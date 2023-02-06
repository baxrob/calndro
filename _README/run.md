
### Install

#### Python Pip

[ with Python version >=3.8 ]


To install and run in one "line"
```
python3 -m venv venv \
    && . venv/bin/activate \
    && pip install -r requirements/base.txt \
    && cp config/eg.env config/.env \           # @todo
    && scripts/reset.sh \                       # @todo
    && ./manage.py runserver 0.0.0.0:8000
```

[note: ppa pyenv .. https://github.com/pyenv/pyenv]

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

_
- [pg, ngx]

```
./manage.py loaddata users schedul

#docker exec -it caldc ./manage.py loaddata users schedul

docker exec -it caldcs ./manage.py loaddata users schedul
```

- minimal ?

ob zo ub : p

<!--
[up down logs exec / $file= $sys=ubu|alp %cmd[exec]]
-->


#### Fixtures

```
```

See [schedul/fixtures/gen.py](schedul/fixtures/gen.py)


#### Envs

[config/eg.env](config/eg.env) contains a variable reference
```
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

/cf
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

\\cf [grip? ghub? breaks on single backslash in code/pre/tilde-triple]

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
\


#### Admin




There is a full Django admin at
```$host/admin```

<img src="_m/admin_scaps/entries.png" width="250"> <img src="_m/admin_scaps/entries_1.png" width="250"> <img src="_m/admin_scaps/events.png" width="250"> <img src="_m/admin_scaps/events_1a.png" width="250"> <img src="_m/admin_scaps/events_1b.png" width="250"> <img src="_m/admin_scaps/events_1c.png" width="250">

<!-- ugh, .tf
<span style="display: inline-block;" align="center"><span style="display: block;">entries</span><img src="_m/admin_scaps/entries.png" width="250"></span> <img src="_m/admin_scaps/entries_1.png" width="250"> <img src="_m/admin_scaps/events.png" width="250"> <img src="_m/admin_scaps/events_1a.png" width="250"> <img src="_m/admin_scaps/events_1b.png" width="250"> <img src="_m/admin_scaps/events_1c.png" width="250">
-->

<br>
