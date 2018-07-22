from contextlib import suppress
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Sum

from .models import Map, Run


def get_latest_map():
    with suppress(Map.DoesNotExist):
        return Map.objects.latest("id")


def get_map_count():
    return Map.objects.count()


def get_total_downloads():
    return Map.objects.aggregate(Sum("download_count"))["download_count__sum"] or 0


def get_date_run_count(date_):
    return Run.objects.filter(
        created_at__range=(date_, date_ + timedelta(days=1))
    ).count()


def get_yesterday_run_count():
    value = cache.get("runs_yesterday_count")
    if value is None:
        from tasks import update_yesterday_runs

        update_yesterday_runs.apply()
        value = cache.get("runs_yesterday_count")
    return value


def get_cached_totals():
    keys = ["total_runs", "total_runtime", "total_playtime"]
    values = cache.get_many(keys)
    if set(keys) != set(values):
        from .tasks import update_totals

        update_totals.apply()
        values = cache.get_many(keys)
    return values
