# encoding: utf-8

#=========================================================================================
# Configuración de la base de datos
#=========================================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'nguru', # Or path to database file if using sqlite3.
        'USER': 'defo', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}
INTERNAL_IPS = ('127.0.0.1',)

