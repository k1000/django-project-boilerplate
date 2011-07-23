# Django project site specific settings
# All non site specific settings should go into the settings.py file
# Copy this file as settings_local.py and adjust it to your site.
# The settings_local.py contains only site specific information and should not
# be part of the svn repository of the project. It should be part of the
# hosting svn repository.

DEBUG = True #TODO set to off for live, staging and preview
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '(xxq$%nk3o!4q_dddddddddddddd_6(6)-0i' #TODO Change on production

#TODO: replace localhost with the domain name of the site
DEFAULT_FROM_EMAIL = 'messenger@localhost'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ADMINS = (
    ('Admin Name', 'admin@example.com'), #TODO
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': '',                           # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                             # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'Canada/Eastern'

INTERNAL_IPS = ('127.0.0.1', )
INTERCEPT_REDIRECTS = False

# Allows for certain Django apps to be installed on a local basis,
# independent of INSTALLED_APPS in the main settings.py file.
LOCAL_INSTALLED_APPS = (
)
