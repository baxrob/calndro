
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
