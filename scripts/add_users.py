#!/usr/bin/env python3

import os
import sys
from getpass import getpass
import django
from django.contrib.auth import get_user_model

cwd = os.getcwd()
sys.path.append(cwd + '/..')
os.environ['DJANGO_SETTINGS_MODULE'] = "config.settings"
django.setup()

User = get_user_model()

while True:
    name = input('Username: ')
    email = input('Email: ')
    password = getpass()
    perms = input('Enter permissions [active, staff, super] (100): ')
    perms = '100' if len(perms) == 0 else perms
    do_create = input('Confirm and create %s %s %s Y/n:'
        % (name, email, perms))
    if do_create in ['n', 'N']:
        continue

    user = User.objects.create_user(name, email, password)
    user.is_active = False if perms[0] == '0' else True
    user.is_staff = True if perms[1] == '1' else False
    user.is_superuser = True if perms[2] == '1' else False
    user.save()
    print(user)

    contin = input('Continue Y/n: ')
    if contin in ['n', 'N']:
        break
