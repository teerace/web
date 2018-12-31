# pylint: disable-all
"""
settings/default.py

Do NOT (!!!) edit this file!
Please override settings in settings/local.py instead,
or use environment variables to override default settings.
"""

import environ
from celery.schedules import crontab
from furl import furl


root = environ.Path(__file__) - 3

# Django settings for teerace project.

env = environ.Env()

environ.Env.read_env(env_file=root(".env"))
BASE_DIR = root()

DEBUG = env.bool("DEBUG", default=False)
DEBUG_TOOLBAR = env("DEBUG_TOOLBAR", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INTERNAL_IPS = ("127.0.0.1",)

DATABASES = {
    "default": env.db(default="postgres://postgres:postgres@postgres:5432/postgres")
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        # "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        #        'BACKEND': 'johnny.backends.memcached.MemcachedCache',
        "LOCATION": "localhost:11211",
    }
}

MAILER_ADDRESS = ""
WEBMASTER_EMAIL = ""

# You have to set this in order to use reCAPTCHA
ENABLE_CAPTCHA = env.bool("ENABLE_CAPTCHA", default=False)
if ENABLE_CAPTCHA:
    RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
    RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
    NOCAPTCHA = env.bool("NOCAPTCHA", default=True)

# Paginator
PAGINATION_DEFAULT_PAGINATION = 20
# ... 2 3 4 [5] 6 7 8 ...
PAGINATION_DEFAULT_WINDOW = 3
# If the last page has 1 object, the object gets attached to previous one instead.
PAGINATION_DEFAULT_ORPHANS = 1
PAGINATION_INVALID_PAGE_RAISES_404 = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = env("MEDIA_ROOT", default=(root - 1)("media"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = env("MEDIA_URL", default="/media/")

COUNTRIES_FLAG_URL = "images/flags/{code}.gif"

STATIC_ROOT = env("STATIC_ROOT", default=(root - 1)("static"))
STATIC_URL = env("STATIC_URL", default="/static/")

# Additional locations of static files
STATICFILES_DIRS = (root("static"),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_FILE_STORAGE = env(
    "DEFAULT_FILE_STORAGE", default="lib.file_storage.OverwriteStorage"
)
GS_BUCKET_NAME = env("GS_BUCKET_NAME", default=None)
GS_DEFAULT_ACL = env("GS_DEFAULT_ACL", default="publicRead")

# Make this unique, and don't share it with anybody.
SECRET_KEY = env("SECRET_KEY", default="foobar")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Message storage backend
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

FIRST_LOGIN_REDIRECT_URL = "/getstarted/"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"

ABSOLUTE_URL_OVERRIDES = {"auth.user": lambda u: "/profile/%s/" % u.id}

GRAVATAR_DEFAULT_IMAGE = "mm"
GRAVATAR_DEFAULT_SIZE = 50
COMMENTS_HIDE_REMOVED = False
COMMENTS_ALLOW_PROFANITIES = True

RESULT_PRECISION = 3

BREADCRUMBS_TEMPLATE = "snippets/breadcrumbs.html"

SESSION_ENGINE = env("SESSION_ENGINE", default="django.contrib.sessions.backends.db")

MIDDLEWARE = ["django.middleware.security.SecurityMiddleware"]

if env.bool("STATICFILES_WHITENOISE", True):
    MIDDLEWARE += ["whitenoise.middleware.WhiteNoiseMiddleware"]

MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "dj_pagination.middleware.PaginationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [root("templates")],
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                "lib.context_processors.settings",
            ),
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "debug": DEBUG,
        },
    }
]

ROOT_URLCONF = "config.urls"
# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "config.wsgi.application"

OUR_APPS = ("race", "accounts", "api", "blog", "home", "stats")

INSTALLED_APPS = (
    "config.apps.DjangoContribAuthConfig",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.admin",
    "django_markwhat",
    "django.contrib.humanize",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "lib",
    "cachalot",
    "django_bootstrap_breadcrumbs",
    "django_gravatar",
    "django_comments",
    "threadedcomments",
    "faq",
    "dj_pagination",
    "webstack_django_sorting",
    "actstream",
    "captcha",
    "rest_framework",
    "config.apps.PinaxBadgesConfig",
) + OUR_APPS

COMMENTS_APP = "threadedcomments"

CELERY_REDIS_URL = env("REDIS_URL", default="")
CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE", default="celery")
CELERY_BROKER_URL_DEFAULT = "redis://redis:6379/1"
if CELERY_REDIS_URL:
    CELERY_BROKER_URL_DEFAULT = furl(CELERY_REDIS_URL).set(path="0").url
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=CELERY_BROKER_URL_DEFAULT)
CELERY_RESULT_BACKEND_DEFAULT = "redis://redis:6379/2"
if CELERY_REDIS_URL:
    CELERY_RESULT_BACKEND_DEFAULT = furl(CELERY_REDIS_URL).set(path="1").url
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=CELERY_RESULT_BACKEND_DEFAULT
)

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
    "totals": {"task": "race.tasks.update_totals", "schedule": crontab(minute="*/15")},
    # everyday, 11:00 PM
    "daily_email_notification": {
        "task": "lib.tasks.send_server_update_notification",
        "schedule": crontab(hour=23, minute=00),
    },
}

SECURE_PROXY_SSL_HEADER_ENABLE = env.bool(
    "SECURE_PROXY_SSL_HEADER_ENABLE", default=False
)
if SECURE_PROXY_SSL_HEADER_ENABLE:
    SECURE_PROXY_SSL_HEADER = (
        env("SECURE_PROXY_SSL_HEADER_NAME", default="HTTP_X_FORWARDED_PROTO"),
        env("SECURE_PROXY_SSL_HEADER_VALUE", default="https"),
    )
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
if SECURE_SSL_REDIRECT:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)

RAVEN_DSN = env("RAVEN_DSN", default="")
if RAVEN_DSN:
    INSTALLED_APPS += ("raven.contrib.django.raven_compat",)
    RAVEN_ENVIRONMENT = env("RAVEN_ENVIRONMENT", default="staging")
    RAVEN_RELEASE = env("RAVEN_RELEASE", default=None)
    RAVEN_CONFIG = {
        "dsn": RAVEN_DSN,
        "transport": "raven.transport.threaded_requests.ThreadedRequestsHTTPTransport",  # noqa
        "environment": RAVEN_ENVIRONMENT,
        "release": RAVEN_RELEASE,
    }
    MIDDLEWARE = [
        "raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware"  # noqa
    ] + MIDDLEWARE

MIN_GAMESERVER_VERSION = 1

GITHUB_API_URL = "https://api.github.com"
GITHUB_USER = "SushiTee"
GITHUB_REPO = "teeworlds"
GITHUB_BRANCH = "teerace-0.6"

REST_FRAMEWORK_ENABLE_BROWSABLE_API = env.bool(
    "REST_FRAMEWORK_ENABLE_BROWSABLE_API", default=False
)
REST_FRAMEWORK_RENDERERS = ("rest_framework.renderers.JSONRenderer",)
if REST_FRAMEWORK_ENABLE_BROWSABLE_API:
    REST_FRAMEWORK_RENDERERS += ("rest_framework.renderers.BrowsableAPIRenderer",)
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": REST_FRAMEWORK_RENDERERS,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "api.v1.authentication.ServerTokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}
