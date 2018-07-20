from datetime import date, datetime, time, timedelta

from celery.task import task

from accounts.models import UserProfile
from race.models import Run

from .models import Chart


@task(ignore_result=True)
def update_daily_charts():
    # everyday, around 0:00 AM
    logger = update_daily_charts.get_logger()
    races_daily, created = Chart.objects.get_or_create(slug="races-daily")
    yesterday = date.today() - timedelta(days=1)
    runs_yesterday = Run.objects.filter(
        created_at__range=(
            datetime.combine(yesterday, time.min),
            datetime.combine(yesterday, time.max),
        )
    ).count()
    races_daily.append(runs_yesterday)

    races_overall, created = Chart.objects.get_or_create(slug="races-overall")
    runs_total = Run.objects.count()
    races_overall.append(runs_total)

    players_daily, created = Chart.objects.get_or_create(slug="players-daily")
    yesterday = date.today() - timedelta(days=1)
    players_yesterday = UserProfile.objects.filter(
        last_connection_at__range=(
            datetime.combine(yesterday, time.min),
            datetime.combine(yesterday, time.max),
        )
    ).count()
    players_daily.append(players_yesterday)

    logger.info("Updated daily charts.")
