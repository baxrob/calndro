#!/bin/sh

# mysql -u bh_cald_0 -p -h mysql.blandhand.net bh_cald_0

host=blandhand.net
domain=cald.$host
dbhost=mysql.$host
dbuser=bh_cald_0
dbname=$dbuser

env_path=../../.bh.env
fromemail="\\\"cald:admin\\\" <bh_admin@${domain}>"
admins="${fromemail},rlb@blandhand.net"
staticroot=../static
dbpw=
emailpw=

if [ -z "$env_path" ]; then
    echo 'env path: '
    #read -e env_path
    env_path="$(bash -c 'read -e x; echo $x')"
    echo $env_path
fi

echo -n 'database password: '
#read -s dbpw
dbpw=$(bash -c 'read -s x; echo $x')
echo

if [ -z "$fromemail" ]; then
    echo -n 'sender email: '
    read fromemail
    echo $fromemail
fi

echo -n 'email password: '
#read -s emailpw
emailpw=$(bash -c 'read -s x; echo $x')
echo

if [ -z "$staticroot" ]; then
    echo 'static root: '
    #read -e staticroot
    staticroot=$(bash -c 'read -e x; echo $x')
    echo $staticroot
fi

key=$(tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c50)

#cat <<END >> "$env_path"
cat <<END

DJANG_SECRET_KEY=$key

ALLOWED_HOSTS=$domain,testserver

STATIC_ROOT="$staticroot"
DJANGO_SERVE_STATIC=1

DATABASE_ENGINE=mysql
DATABASE_NAME=$dbname
DATABASE_USER=$dbuser
DATABASE_PASSWORD=$dbpw
DATABASE_HOST=$dbhost
#DATABASE_PORT=

DJANGO_ADMINS="$admins"
DJANGO_SERVER_EMAIL="$freomemail"
DJANGO_DEFAULT_FROM_EMAIL="$fromemail"

EMAIL_SUBJECT_PREFIX='[calndro] '
#EMAIL_USE_LOCALTIME=False
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.dreamhost.com
EMAIL_PORT=465
EMAIL_HOST_USER="$fromemail"
EMAIL_HOST_PASSWORD=$emailpw
#EMAIL_TIMEOUT=
#EMAIL_USE_TLS=
#EMAIL_USE_SSL=
#EMAIL_SSL_KEYFILE=
#EMAIL_SSL_CERTFILE=

END

# stage/entrypoint.sh:16:./manage.py collectstatic --noinput
