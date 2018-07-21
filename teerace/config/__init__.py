# https://github.com/docker-library/python/issues/211
import threading

threading.stack_size(2 * 1024 * 1024)

from ._celery import app as celery_app

__all__ = ["celery_app"]
