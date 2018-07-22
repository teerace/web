import json
from datetime import date, datetime
from time import mktime
from time import time as timestamp

from actstream.models import Action
from annoying.decorators import ajax_request
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import utc

from accounts.services import get_latest_actions, get_latest_user, get_user_count
from blog.services import latest_entries
from race.services import (
    get_date_run_count,
    get_latest_map,
    get_map_count,
    get_total_downloads,
    get_cached_totals,
    get_yesterday_run_count,
)


def homepage(request):
    messages.info(request, "Please enable Javascript.", extra_tags="javascript")

    return render(
        request,
        "home.html",
        {
            "latest_entries": latest_entries(),
            "latest_user": get_latest_user(),
            "user_count": get_user_count(),
            "latest_map": get_latest_map(),
            "map_count": get_map_count(),
            "user_actions": get_latest_actions(),
            "runs_today": get_date_run_count(date.today()),
            "runs_yesterday": get_yesterday_run_count(),
            **get_cached_totals(),
            "total_downloads": get_total_downloads(),
        },
    )


def stream_since_json(request, since_timestamp):
    # I would have used @ajax_request, but default JSON serializer
    # is not able to deal with datetime.date objects.
    dthandler = (
        lambda obj: mktime(obj.timetuple()) * 1000
        if isinstance(obj, datetime)
        else None
    )

    since_datetime = datetime.fromtimestamp(float(since_timestamp) / 1000, tz=utc)
    new_actions = Action.objects.filter(timestamp__gt=since_datetime).order_by(
        "-timestamp"
    )[:10]
    response_data = []
    for action in new_actions:
        response_data.append(
            {
                "actor_id": action.actor.id if action.actor else None,
                "actor_repr": str(action.actor),
                "actor_url": action.actor.get_absolute_url()
                if action.actor.get_absolute_url()
                else action.actor_url,
                "verb": action.verb,
                "action_object_id": action.action_object.id
                if action.action_object
                else None,
                "action_object_repr": str(action.action_object),
                "target_id": action.target.id if action.target else None,
                "target_repr": str(action.target),
                "target_url": action.target.get_absolute_url()
                if action.target and action.target.get_absolute_url()
                else None,
                "timesince": action.timesince(),
                "timestamp": action.timestamp,
            }
        )
    response_data = json.dumps({"new_actions": response_data}, default=dthandler)
    return HttpResponse(response_data, content_type="application/json")


@ajax_request
def server_timestamp(request):
    return {"timestamp": int(timestamp()) * 1000}
