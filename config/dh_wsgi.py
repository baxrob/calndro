import sys, os

INTERP = "/home/bhand/cald.blandhand.net/venv/bin/python3"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/calndro')

sys.path.insert(0,cwd+'/venv/bin')
sys.path.insert(0,cwd+'/venv/lib/%pyver/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "config.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import logging

logfilename = os.path.join(cwd, 'passenger_wsgi.log')

handler = logging.FileHandler(logfilename)
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

