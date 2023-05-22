from pathlib import Path
import os

from email.utils import getaddresses, parseaddr
import environ


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.smart_cast = False

environ.Env.read_env(env.str(
    'ENV_PATH', 
    Path(__file__).resolve().parent / '.env'
))

# SECURITY WARNING: keep the secret key used in production secret!
# python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# tr -dc 'a-z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c50
# base64 /dev/urandom | head -c50
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', [])

HOST_DOMAIN = env.str('HOST_DOMAIN', '')

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
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
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

if DEBUG:
    print('### BASE_DIR ###', BASE_DIR)
    print('db', DATABASES)


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = '/static/'

STATIC_ROOT = env.str('STATIC_ROOT', None)


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#ADMINS = getaddresses([env('DJANGO_ADMINS')])
ADMINS = getaddresses(env.list('DJANGO_ADMINS'))

DEFAULT_FROM_EMAIL = parseaddr(
    env.str('DJANGO_DEFAULT_FROM_EMAIL', 'admin@localhost'))
SERVER_EMAIL = parseaddr(env.str('DJANGO_SERVER_EMAIL', 'admin@localhost'))

if DEBUG:
    print('admins:', 'env:', env.list('DJANGO_ADMINS'), 'dj:', ADMINS)
    print('from:', DEFAULT_FROM_EMAIL, 'server:', SERVER_EMAIL)

EMAIL_SUBJECT_PREFIX = env.str('EMAIL_SUBJECT_PREFIX', '[calndro] ')
EMAIL_USE_LOCALTIME = env.str('EMAIL_USE_LOCALTIME', False)

# console filebased smtp locmem dummy 
EMAIL_BACKEND = 'django.core.mail.backends.{}.EmailBackend'.format(
    env.str('EMAIL_BACKEND', 'console')
)
EMAIL_FILE_PATH = env.str('EMAIL_FILE_PATH', '/tmp/cald-mail')

EMAIL_HOST = env.str('EMAIL_HOST', '')
EMAIL_PORT = env.str('EMAIL_PORT', '')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', False)
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', False)
EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', 5)

EMAIL_SSL_KEYFILE = env.str('EMAIL_SSL_KEYFILE', '')
EMAIL_SSL_CERTFILE = env.str('EMAIL_SSL_CERTFILE', '')


REST_FRAMEWORK = {
    #'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}


# Schedul

EMAILTOKEN_EXPIRATION_DAYS = 5

