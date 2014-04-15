# Django settings for nguru project.
import sys
import os
from os.path import abspath, dirname, join


SETTINGS_PATH = dirname(__file__)  # Settings es un modulo
PROJECT_ROOT = abspath(join(SETTINGS_PATH, '../..'))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

from django.utils.translation import ugettext_lazy as _

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'txscada',                      # Or path to database file if using sqlite3.
#        'USER': '',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#    }
#}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 1


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = join(PROJECT_ROOT , 'static', 'media')


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(PROJECT_ROOT, 'static-content')

BASE_URL = 'smve/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/{}static/'.format(BASE_URL)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = STATIC_URL + 'media/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #join(PROJECT_ROOT, 'static-conent'),
    'static',
    join(PROJECT_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x%k&amp;2=1prox)=rkc8@vlqa#yp4!27gm=fq6cl5xp_v8welgmts'

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
    'debug_toolbar.middleware.DebugToolbarMiddleware',

)

MIDDLEWARE_CLASSES += 'dealer.contrib.django.staff.Middleware',


ROOT_URLCONF = 'nguru.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'nguru.wsgi.application'
if os.environ['DJANGO_SETTINGS_MODULE'].startswith('nguru.nguru'):
    WSGI_APPLICATION = 'nguru.%s' % WSGI_APPLICATION

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    # Django admin tools
    #'admin_tools',
    #'admin_tools.theming',
    #'admin_tools.menu',
    #'admin_tools.dashboard',
    'crispy_forms',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'south',
    # Graphical Query Browser

    'django_extensions',
    'django_socketio',
    'debug_toolbar',
    'django_nose',

    'apps.mara',
    'apps.hmi',
    'apps.api',

    'apps.research',

    #'admin_bootstrap',
    'django_qbe',
    'django_qbe.savedqueries',

    'object_tools',
    'django.contrib.admin',

    'django_js_reverse',
    # Django Mailer
    'mailer',

    'constance',

    'constance.backends.database',
)

try:
    import gunicorn
except ImportError as e:
    pass
else:
    INSTALLED_APPS += ('gunicorn',)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },

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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'datalogger': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'factory': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'commands': {
            'handlers': ['console', ],
            'level': 'DEBUG',
            'propagate': True
        },
        'excel_import': {
            'handlers': ['console', ],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}


#=========================================================================================
# Debug Toolbar
#=========================================================================================

def show_toolbar(request):
    from constance import config
    debug_users = set(map(lambda x: x.strip(), config.DEBUG_USERS.split(',')))
    if request.user and request.user.username in debug_users:
        return True
    return False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

#=========================================================================================
# Testing Config
#=========================================================================================

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    #'--nologcapture', '--nocapture',
    '--with-id', '--logging-clear-handlers',
    '--with-progressive', '--progressive-function-color=1', '--progressive-bar-filled=2',
    #'--with-noseprofhooks',
    #'--cprofile-stats-erase',
    #'--cprofile-stats-file=stats.stats',
    #'--processes=8'
]


LOCALE_PATHS = (
    join(PROJECT_ROOT, 'conf/locale'),
)

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/' + BASE_URL


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "dealer.contrib.django.staff.context_processor",
    "constance.context_processors.config",

)


AUTH_PROFILE_MODULE = 'hmi.UserProfile'


CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

email_template = '''Estimado
Se ha producido un evento {{ event }} a las {{ event.timestamp|date:config.EVENT_DATE_FORMAT }}
'''

sms_template = '''Estimado
Se ha producido un evento {{ event }} a las {{ event.timestamp|date:config.EVENT_DATE_FORMAT }}
'''

CONSTANCE_CONFIG = {
    'EVENT_0_EMAIL': ('admin', _('Users to be notified of a Event type 0 by email. '
                                 'Comma separated.')),
    'EVENT_3_EMAIL': ('admin', _('Users to be notified of a Event type 3 by email. '
                                 'Comma separated.')),
    'EVENT_0_SMS': ('admin', _('Users to be notified of a Event type 0 by SMS. '
                               'Comma separated')),
    'EVENT_3_SMS': ('admin', _('Users to be notified of a Event type 3 by SMS. '
                               'Comma separated')),
    'DEBUG_USERS': ('nahuel', _('Users that have debug toolbar enabled')),
    'TEMPLATE_EMAIL': (email_template, _('Email template.')),
    'TEMPLATE_SMS': (sms_template, _('SMS template.')),
    'EVENT_DATE_FORMAT': ('G:i:s.u d/m/Y', _('Format for date in SMS and email.'))
}
