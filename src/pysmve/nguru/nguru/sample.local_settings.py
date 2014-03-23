# encoding: utf-8

#=========================================================================
# Configuración de la base de datos
#=========================================================================
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{database}',  # Or path to database file if using sqlite3.
        'USER': '{user}',  # Not used with sqlite3.
        'PASSWORD': '{password}',  # Not used with sqlite3.
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': 'localhost',
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
        #'OPTIONS': {
        #    'init_command': "SET lc_messages TO 'en_US.UTF-8';"
        #}
    }
}

INTERNAL_IPS = ('127.0.0.1',)

SOUTH_TESTS_MIGRATE = False


NOSE_ARGS = [
    '--nologcapture', '--nocapture',
    '--with-id', '--logging-clear-handlers',
    '--with-progressive', '--progressive-function-color=1', '--progressive-bar-filled=2',
    #'--with-noseprofhooks',
    #'--cprofile-stats-erase',
    #'--cprofile-stats-file=stats.stats',
    #'--processes=8'
]


# PATH independent code
try:
    import nguru.wsgi
    WSGI_APPLICATION = 'nguru.wsgi.application'
    ROOT_URLCONF = 'nguru.urls'
except ImportError:
    WSGI_APPLICATION = 'nguru.nguru.wsgi.application'
    ROOT_URLCONF = 'nguru.nguru.urls'
