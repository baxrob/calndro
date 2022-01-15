#!/bin/sh

set -ex

./manage.py makemigrations
./manage.py migrate
./manage.py loaddata users
./manage.py loaddata schedul

