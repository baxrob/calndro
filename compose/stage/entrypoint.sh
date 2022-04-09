#!/bin/sh


if [ "$DATABASE_ENGINE" == postgresql ]; then
    echo -n "wait for pg ."
    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
        printf "."
        sleep 1
    done
    printf "\n"
fi

set -ex

./manage.py migrate
./manage.py collectstatic --noinput

gunicorn --bind 0.0.0.0:8000 --log-file - --log-level debug config.wsgi:application
