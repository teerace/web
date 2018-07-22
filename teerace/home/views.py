import json
from datetime import date, datetime
from time import mktime
from time import time as timestamp

from annoying.decorators import ajax_request
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import utc

from accounts.services import get_latest_actions, get_latest_user, get_user_count
from blog.services import latest_entries
from race.services import (
    get_cached_totals,
    get_date_run_count,
    get_latest_map,
    get_map_count,
    get_total_downloads,
    get_yesterday_run_count,
)

from .services import actions_to_json, get_new_actions


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
            "total_downloads": get_total_downloads(),
            **get_cached_totals(),
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

    since = datetime.fromtimestamp(float(since_timestamp) / 1000, tz=utc)
    new_actions = get_new_actions(since)

    response_data = json.dumps(
        {"new_actions": actions_to_json(new_actions)}, default=dthandler
    )
    return HttpResponse(response_data, content_type="application/json")


@ajax_request
def server_timestamp(request):
    return {"timestamp": int(timestamp()) * 1000}
