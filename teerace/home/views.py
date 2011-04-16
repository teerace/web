import json
from datetime import date, datetime, time
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from blog.models import Entry
from race.models import Map, Run
from race import tasks
from annoying.decorators import render_to
from actstream.models import Action


@render_to('home.html')
def homepage(request):
	try:
		latest_entries = Entry.objects.filter(status=Entry.PUBLISHED_STATUS) \
			.order_by('-created_at').select_related()[:2]

		if latest_entries.count() > 1:
			if not latest_entries[0].is_micro and not latest_entries[1].is_micro:
				latest_entries = latest_entries[:1]
	except Entry.DoesNotExist:
		latest_entries = None

	user_base = User.objects.exclude(is_active=False)
	try:
		latest_user = user_base.latest('id')
	except User.DoesNotExist:
		latest_user = None
	user_count = user_base.count()

	try:
		latest_map = Map.objects.latest('id')
	except Map.DoesNotExist:
		latest_map = None
	map_count = Map.objects.count()

	user_actions = Action.objects.order_by('-timestamp')[:10]

	today = date.today()
	runs_today = Run.objects.filter(created_at__range=
		(datetime.combine(today, time.min),
		datetime.combine(today, time.max)))

	runs_yesterday = cache.get('runs_yesterday')
	if runs_yesterday is None:
		tasks.update_yesterday_runs.apply()
		runs_yesterday = cache.get('runs_yesterday')

	total_runs = cache.get('total_runs')
	if total_runs is None:
		tasks.update_totals.apply()
		total_runs = cache.get('total_runs')

	total_runtime = cache.get('total_runtime')
	if total_runtime is None:
		tasks.update_totals.apply()
		total_runtime = cache.get('total_runtime')

	total_playtime = cache.get('total_playtime')
	if total_playtime is None:
		tasks.update_totals.apply()
		total_playtime = cache.get('total_playtime')

	total_downloads = Map.objects.aggregate(
		Sum('download_count')
	)['download_count__sum']

	return {
		'latest_entries': latest_entries,
		'latest_user': latest_user,
		'user_count': user_count,
		'latest_map': latest_map,
		'map_count': map_count,
		'user_actions': user_actions,
		'run_count': total_runs,
		'runs_today': runs_today,
		'runs_yesterday': runs_yesterday,
		'total_runtime': total_runtime,
		'total_playtime': total_playtime,
		'total_downloads': total_downloads,
	}


def stream_since_json(request, since_timestamp):
	# I would have used @ajax_request, but default JSON serializer
	# is not able to deal with datetime.date objects.
	dthandler = lambda obj: time.mktime(obj.timetuple())*1000 \
		if isinstance(obj, datetime.date) else None

	since_datetime = datetime.from_timestamp(since_timestamp)
	new_actions = Action.objects.filter(timestamp__gt=since_datetime)
	response_data = json.dumps(
		{'new_actions': new_actions},
		default=dthandler,
	)
	return HttpResponse(response_data, mimetype="application/json")
