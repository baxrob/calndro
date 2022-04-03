#!/bin/sh

set -ex

#./manage.py makemigrations 
#./manage.py makemigrations schedul
./manage.py migrate
./manage.py loaddata users
./manage.py loaddata schedul

