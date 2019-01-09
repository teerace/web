#!/bin/sh
set -e

if [ "$1" = 'shell' ]; then
    shift
    set -- manage shell_plus $@
elif [ "$1" = 'runserver' ]; then
    shift
    set -- manage runserver 0.0.0.0:8000 $@
elif [ "$1" = 'runserver_plus' ]; then
    shift
    set -- manage runserver_plus 0.0.0.0:8000 $@
fi


if [ "$1" = 'manage' ]; then
    shift
    exec python -Wd manage.py $@
elif [ "$1" = 'uwsgi' ]; then
    exec uwsgi --ini=run/uwsgi.ini
elif [ "$1" = 'celery' ]; then
    exec celery -A config worker
elif [ "$1" = 'beat' ]; then
    exec celery -A config beat
elif [ "$1" = 'isort' ]; then
    shift
    exec isort -y $@
elif [ "$1" = 'black' ]; then
    exec black ..
elif [ "$1" = 'flake8' ]; then
    exec flake8 ..
elif [ "$1" = 'mypy' ]; then
    exec mypy .
elif [ "$1" = 'now-runner' ]; then
    python manage.py migrate && exec python manage.py runserver 0.0.0.0:8000
fi

exec "$@"
