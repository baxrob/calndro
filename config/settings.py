from pathlib import Path

import environ


# Build paths inside the project like this: BASE_DIR / 'subdir'.
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
SECRET_KEY = 'django-insecure-vp9+ja5i_bdgho0c0ioh#5s^=-9el_e0t)om&@bh_ux9+)@#th'
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = []
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
    #'schedul',
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
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
DATABASES = {
    'default': env.db_url()
}

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

'''

CACHES = {
    'default': env.cache_url()
}

CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_COOKIE_SAME_SITE = 'Strict'
CSRF_COOKIE_SECURE = True

CACHES = {
}

USE_ETAGS = True

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

EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_USE_TLS
EMAIL_USE_SSL

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
