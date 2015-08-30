# Django settings for stationspinner project.

DEBUG = False


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    },
    'sde': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost',]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q5=dq_42ao71t3sut5wty)&wvi@25hw%yx)yahrhph33a@7qhz'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'stationspinner.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'stationspinner.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    # external apps
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Stationspinner apps
    'stationspinner.sde',
    'stationspinner.universe',
    'stationspinner.accounting',
    'stationspinner.character',
    'stationspinner.corporation',
    'stationspinner.evecentral',
    'stationspinner.evemail',
    'registration',
    'bootstrapform',

]

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

# Celery settings

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
AUTH_USER_MODEL = 'accounting.Capsuler'

# Django rest framework settings

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 100
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

### Django registration
ACCOUNT_ACTIVATION_DAYS = 3
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25



EVEMAIL_SEARCH_LANGUAGES = (
    'english',
)

# Market stuff
DEFAULT_MARKET = 'Jita'
MARKET_VALUE_SUPERS = {
    11567:          100000000000, #Avatar
    671:            100000000000, #Erebus
    3764:           100000000000, #Leviathan
    23773:          100000000000, #Ragnarok
    3514:           100000000000, #Revenant
    23913:          20000000000,  #Nyx
    22852:          20000000000,  #Hel
    23917:          20000000000,  #Wyvern
    23919:          20000000000,  #Aeon
}

CELERY_TIMEZONE = 'UTC'
CELERY_IGNORE_RESULT = True
BROKER_TRANSPORT_OPTIONS = {
    'fanout_prefix': True,
    'fanout_patterns': True
    }

from datetime import timedelta
TASK_INTERVALS = {
    'evecentral.update_all_markets': timedelta(hours=6),
    'universe.update_universe': timedelta(hours=24),
    'accounting.update_capsuler_keys': timedelta(hours=24),
    'accounting.update_all_sheets': timedelta(hours=24),
    'accounting.update_all_apidata': timedelta(minutes=30),
}


# Local settings ...

try:
    from local_settings import *
except:
    pass

TEMPLATE_DEBUG = DEBUG
if DEBUG:
    LOGGING['handlers']['console'] = {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler'
    }

DATABASE_ROUTERS = ['stationspinner.dbrouter.DBRouter',]


CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'evecentral.update_all_markets': {
        'task': 'evecentral.update_all_markets',
        'schedule': TASK_INTERVALS['evecentral.update_all_markets']
    },
    'universe.update_universe': {
        'task': 'universe.update_universe',
        'schedule': TASK_INTERVALS['universe.update_universe']
    },
    'accounting.update_capsuler_keys': {
        'task': 'accounting.update_capsuler_keys',
        'schedule': TASK_INTERVALS['accounting.update_capsuler_keys']
    },
    'accounting.update_all_sheets': {
        'task': 'accounting.update_all_sheets',
        'schedule': TASK_INTERVALS['accounting.update_all_sheets']
    },
    'accounting.update_all_apidata': {
        'task': 'accounting.update_all_apidata',
        'schedule': TASK_INTERVALS['accounting.update_all_apidata']
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )

}
