import json
from datetime import date, datetime, time
from time import mktime, time as timestamp
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from blog.models import Entry
from race.models import Map, Run
from race import tasks
from annoying.decorators import render_to, ajax_request
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

	messages.info(request, "Please enable Javascript.", extra_tags="javascript")

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
	dthandler = lambda obj: mktime(obj.timetuple())*1000 \
		if isinstance(obj, datetime) else None

	since_datetime = datetime.fromtimestamp(float(since_timestamp)/1000)
	new_actions = Action.objects.filter(timestamp__gt=since_datetime) \
		.order_by('-timestamp')[:10]
	response_data = []
	for action in new_actions:
		response_data.append({
			'actor_id': action.actor.id if action.actor else None,
			'actor_repr': str(action.actor),
			'actor_url': action.actor.get_absolute_url() if \
				action.actor.get_absolute_url() else action.actor_url,
			'verb': action.verb,
			'action_object_id': action.action_object.id \
				if action.action_object else None,
			'action_object_repr': str(action.action_object),
			'target_id': action.target.id if action.target else None,
			'target_repr': str(action.target),
			'target_url': action.target.get_absolute_url() if action.target and
				action.target.get_absolute_url() else None,
			'timesince': action.timesince(),
			'timestamp': action.timestamp,
		})
	response_data = json.dumps(
		{'new_actions': response_data},
		default=dthandler,
	)
	return HttpResponse(response_data, content_type="application/json")

@ajax_request
def server_timestamp(request):
	return {'timestamp': int(timestamp())*1000}
