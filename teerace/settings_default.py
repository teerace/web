# pylint: disable-all
"""
settings_default.py

Do NOT (!!!) edit this file!
Please override settings in settings_local.py instead.
"""

import os, sys
from django import contrib
# Django settings for teerace project.

PROJECT_DIR = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_DIR)

DEBUG = False
#TEMPLATE_DEBUG = False
TEMPLATE_CACHING = True
BETA = False

INTERNAL_IPS = ('127.0.0.1',)

ADMINS = (
#   ('John Doe', 'joe@doe.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'.
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': PROJECT_DIR + '/teerace.sqlite',
        # Not used with sqlite3.
        'USER': '',
        # Not used with sqlite3.
        'PASSWORD': '',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    }
}

# New CACHES setting. Waiting for johnny-cache.
CACHES = {
    'default': {
#       'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'BACKEND': 'johnny.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
    }
}
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_teerace'

MAILER_ADDRESS = ''
WEBMASTER_EMAIL = ''

# You have to set this in order to use reCAPTCHA
ENABLE_CAPTCHA = False
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_USE_SSL = True
RECAPTCHA_OPTIONS = {}
RECAPTCHA_VALIDATION_OVERRIDE = False

# Paginator
PAGINATION_DEFAULT_PAGINATION = 20
# ... 2 3 4 [5] 6 7 8 ...
PAGINATION_DEFAULT_WINDOW = 3
# If the last page has 1 object, the object gets attached to previous one instead.
PAGINATION_DEFAULT_ORPHANS = 1
PAGINATION_INVALID_PAGE_RAISES_404 = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

COUNTRIES_FLAG_URL = 'images/flags/{code}.gif'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(contrib.__path__[0], 'admin', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'foobar'

import djcelery
from celery.schedules import crontab
djcelery.setup_loader()

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_IMPORTS = ("race.tasks", "stats.tasks", "lib.tasks")
CELERYBEAT_SCHEDULE = {
    # everyday, 4:30 AM
    "points_history": {
        "task": "race.tasks.update_user_points_history",
        "schedule": crontab(hour=4, minute=30),
    },
    # everyday, 0:30 AM
    "yesterday_runs": {
        "task": "race.tasks.update_yesterday_runs",
        "schedule": crontab(hour=0, minute=30),
    },
    # everyday, 0:32 AM
    "daily_charts": {
        "task": "stats.tasks.update_daily_charts",
        "schedule": crontab(hour=0, minute=32),
    },
    # every 15 minutes
    "totals": {
        "task": "race.tasks.update_totals",
        "schedule": crontab(minute="*/15"),
    },
    # everyday, 11:00 PM
    "daily_email_notification": {
        "task": "lib.tasks.send_server_update_notification",
        "schedule": crontab(hour=23, minute=00),
    },
}
MAN_IN_BLACKLIST = ('djcelery_taskstate',
    'djcelery_workerstate')


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# User profile model
AUTH_PROFILE_MODULE = 'accounts.UserProfile'

# Message storage backend
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

FIRST_LOGIN_REDIRECT_URL = '/getstarted/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/profile/%s/" % u.id,
}

GRAVATAR_DEFAULT_IMAGE = "mm"
GRAVATAR_DEFAULT_SIZE = 50
COMMENTS_HIDE_REMOVED = False
COMMENTS_ALLOW_PROFANITIES = True

RESULT_PRECISION = 3

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

MIDDLEWARE_CLASSES = (
    #'johnny.middleware.LocalStoreClearMiddleware',
    #'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.transaction.TransactionMiddleware',
    # see https://bitbucket.org/jmoiron/johnny-cache/issue/17/
    #'johnny.middleware.CommittingTransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(PROJECT_DIR, 'templates/piston'),
        ],
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'lib.context_processors.settings',
            ),
            'loaders': [
                'admin_tools.template_loaders.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
            'debug': DEBUG,
        },
    },
]

ROOT_URLCONF = 'teerace.urls'
# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'teerace.wsgi.application'

OUR_APPS = (
    'race',
    'accounts',
    'api',
    'blog',
    'home',
    'stats',
)

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'apps.DjangoContribAuthConfig',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django_markwhat',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'lib',
    'cachalot',
    'crumbs',
    'django_gravatar',
    'django_comments',
    'threadedcomments',
    'faq',
    'pagination',
    'sorting',
    'actstream',
    'piston',
    'recaptcha_works',
    'apps.BrabeionConfig',
    'djcelery',
) + OUR_APPS

COMMENTS_APP = 'threadedcomments'

TEST_RUNNER = 'local_tests.LocalTestSuiteRunner'

ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'

MIN_GAMESERVER_VERSION = 1

GITHUB_API_URL = 'https://api.github.com'
GITHUB_USER = 'SushiTee'
GITHUB_REPO = 'teeworlds'
GITHUB_BRANCH = 'teerace-0.6'
