# Django project settings file
# This file should be part of the project repository of the project and should not
# contains any site-specific information.
# Site-specific information (database name/login/password for example) should be
# in the settings_local.py file and should not be added to the project repository

import os

SITE_ID = 1

USE_I18N = True

LANGUAGE_CODE = 'en'

gettext = lambda s: s
LANGUAGES = (('en', gettext('English')),)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'urls'


PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media/')

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static/')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates/'),
)

FILE_UPLOAD_PERMISSIONS = 0664


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',

)


# import local settings overriding the defaults
try:
    from settings_local import *
except ImportError:
    import sys
    sys.stderr.write( "local settings not available\n" )
else:
    try:
        INSTALLED_APPS += LOCAL_INSTALLED_APPS
    except NameError:
        pass

    try:
        MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE_CLASSES
    except NameError:
        pass

