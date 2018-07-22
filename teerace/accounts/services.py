from contextlib import suppress

from actstream.models import Action
from django.contrib.auth import get_user_model


User = get_user_model()

active_users = User.objects.exclude(is_active=False)


def get_latest_user():
    with suppress(User.DoesNotExist):
        return active_users.latest("id")


def get_user_count():
    return active_users.count()


def get_latest_actions():
    return Action.objects.order_by("-timestamp")[:10]
