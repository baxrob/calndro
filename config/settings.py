from pathlib import Path

import environ


#
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
#env = environ.Env(interpolate=True)
env.smart_cast = False
#import ipdb; ipdb.set_trace()
environ.Env.read_env(env.str(
    'ENV_PATH', 
    Path(__file__).resolve().parent / '.env'
))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', False)
print('dbg', DEBUG)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', [])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'schedul.apps.SchedulConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# X: s/3.2/3...
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{}'.format(
            env.str('DATABASE_ENGINE', 'sqlite3')
        ),
        'NAME': env.str('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': env.str('DATABASE_USER', ''),
        'PASSWORD': env.str('DATABASE_PASSWORD', ''),
        'HOST': env.str('DATABASE_HOST', ''),
        'PORT': env.str('DATABASE_PORT', '')
    }
}
#DATABASES = {
#    'default': env.db_url(
#        default='{}{}'.format('sqlite:///', str(BASE_DIR / 'db.sqlite3'))
#    )
#}
print('db', DATABASES)
print('### BASE_DIR ###', BASE_DIR)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# X: ? cull since this is just an api ?
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#

DEFAULT_FROM_EMAIL = env.str('DJANGO_DEFAULT_FROM_EMAIL', 'admin@localhost')

EMAIL_SUBJECT_PREFIX = env.str('EMAIL_SUBJECT_PREFIX', '[calndro] ')
EMAIL_USE_LOCALTIME = env.str('EMAIL_USE_LOCALTIME', False)

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.{}.EmailBackend'.format(
    env.str('EMAIL_BACKEND', 'console')
)
EMAIL_FILE_PATH = env.str('EMAIL_FILE_PATH', '/tmp/cald-mail')

EMAIL_HOST = env.str('EMAIL_HOST', '')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env.str('EMAIL_USE_TLS', '')
EMAIL_USE_SSL = env.str('EMAIL_USE_SSL', '')
EMAIL_TIMEOUT = env.str('EMAIL_TIMEOUT', '')

EMAIL_SSL_KEYFILE = env.str('EMAIL_SSL_KEYFILE', '')
EMAIL_SSL_CERTFILE = env.str('EMAIL_SSL_CERTFILE', '')


'''
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/cald-mail'
#EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_CONFIG = env.email_url('EMAIL_CONFIG')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD

EMAIL_USE_TLS
EMAIL_USE_SSL
EMAIL_TIMEOUT
EMAIL_SSL_KEYFILE
EMAIL_SSL_CERTFILE

EMAIL_SUBJECT_PREFIX
EMAIL_USE_LOCALTIME

from email.utils import parseaddr

ADMINS = tuple(parseaddr(email) for email in env.list('DJANGO_ADMINS'))

EMAIL_CONFIG = env.email_url('EMAIL_CONFIG')

# DJANGO_ADMINS=Blake:blake@cyb.org,Alice:alice@cyb.org
ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS')]

# or use more specific function

from email.utils import getaddresses

# DJANGO_ADMINS=Alice Judge <alice@cyb.org>,blake@cyb.org
ADMINS = getaddresses([env('DJANGO_ADMINS')])

# another option is to use parseaddr from email.utils

# DJANGO_ADMINS="Blake <blake@cyb.org>, Alice Judge <alice@cyb.org>"
from email.utils import parseaddr

ADMINS = tuple(parseaddr(email) for email in env.list('DJANGO_ADMINS'))

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_USE_TLS
EMAIL_USE_SSL

'''


REST_FRAMEWORK = {
    # X: ..
    #'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

'''
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],

CACHES = {
    'default': env.cache_url()
}

CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_COOKIE_SAME_SITE = 'Strict'
CSRF_COOKIE_SECURE = True

CACHES = {
}

USE_ETAGS = True




USE_I18N = False
USE_L10N = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'all.log'
        },
    },
        'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['file'],
            #'formatter': 'verbose',
        },
    },

    'formatters': {
        'verbose': {
            #'format': '{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'format': '{name} {levelname} {asctime} {module} {process:d}'
                ' {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },

    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
'''
