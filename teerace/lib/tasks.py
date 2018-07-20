from datetime import datetime, timedelta

import requests
from celery.task import task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mass_mail
from django.utils import timezone


@task(ignore_result=True)
def send_server_update_notification():
    r = requests.get(
        "/".join(
            settings.GITHUB_API_URL,
            "repos",
            settings.GITHUB_USER,
            settings.GITHUB_REPO,
            "commits",
            settings.GITHUB_BRANCH,
        )
    )
    data = r.json()
    sha = data["sha"]
    author = data["commit"]["author"]["name"]

    send_mail = False
    teerace_server_sha = cache.get("teerace_server_sha")
    if teerace_server_sha is None:
        date = datetime.strptime(data["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        now = timezone.now()
        if now - date < timedelta(
            days=1
        ):  # only do this if the last commit is not older than one day to prevent spam mails
            send_mail = True
    else:
        if sha != teerace_server_sha:
            send_mail = True

    if send_mail:
        from race.models import Server

        cache.set("teerace_server_sha", sha, timeout=None)

        if not settings.DEFAULT_FROM_MAIL:
            return

        # only notify people with servers online
        servers_online = Server.objects.filter(
            last_connection_at__gte=(timezone.now() - timedelta(minutes=10))
        )
        users = []
        for server in servers_online:
            users.append(server.maintained_by)

        if users:
            users = set(users)
            messages = [
                (
                    "Teerace: New server available",
                    "Hello {username}\r\n\r\nThere is a new version of the "
                    "teerace server available.\r\n\r\nThe latest commit with "
                    'the message "{commit_message}" was done by {commiter}.'
                    "\r\nPlease decide for yourself if it is necessary to "
                    "compile the new version. For more information visit {url}"
                    "\r\n\r\ncheers\r\nTeerace team".format(
                        username=user.username,
                        commit_message=data["commit"]["message"],
                        commiter=author,
                        url=data["html_url"],
                    ),
                    settings.DEFAULT_FROM_MAIL,
                    [user.email],
                )
                for user in users
            ]
            send_mass_mail(messages, fail_silently=not settings.DEBUG)
