from datetime import date, datetime, time, timedelta
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list_detail import object_list
from accounts.models import UserProfile
from blog.models import Entry
from race.models import Map, MapType, Run, BestRun, Server
from race import badges, tasks
from annoying.decorators import render_to


@render_to('home.html')
def homepage(request):
	try:
		latest_entry = Entry.objects.exclude(is_published=False) \
			.select_related().latest()
	except Entry.DoesNotExist:
		latest_entry = None

	users = list(User.objects.exclude(is_active=False) \
		.select_related())

	if request.user.is_authenticated():
		user_runs = Run.objects.filter(user=request.user) \
			.order_by('-created_at')[:5]
	else:
		user_runs = []

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

	total_playtime = cache.get('total_playtime')
	if total_playtime is None:
		tasks.update_totals.apply()
		total_playtime = cache.get('total_playtime')

	total_downloads = Map.objects.aggregate(
		Sum('download_count')
	)['download_count__sum']

	return {
		'latest_entry': latest_entry,
		'users': users,
		'maps': list(Map.objects.all()),
		'user_runs': user_runs,
		'run_count': total_runs,
		'runs_today': runs_today,
		'runs_yesterday': runs_yesterday,
		'total_playtime': total_playtime,
		'total_downloads': total_downloads,
	}


def ranks(request):
	# exclude banned users from rank
	# (that user shouldn't have any points anyway, just a precaution)
	users = UserProfile.objects.filter(points__gt=0) \
		.exclude(user__is_active=False).extra(
		select = {'_position':
			"SELECT COUNT(*)+1 FROM accounts_userprofile s "
			"WHERE s.points > accounts_userprofile.points"
		},
		order_by = ['_position']
	)
	total_playtime = Run.objects.aggregate(Sum('time'))['time__sum']
	total_runs = Run.objects.count()
	extra_context = {
		'total_playtime': total_playtime,
		'total_runs': total_runs,
	}
	return object_list(request, queryset=users, template_name='race/ranks.html',
		extra_context=extra_context)


def ranks_map_list(request):
	maps = Map.objects.all().select_related()
	return object_list(request, queryset=maps,
		template_name='race/ranks_map_list.html')


# actually, it's a list of records of a particular map
def ranks_map_detail(request, map_id):
	map_obj = get_object_or_404(Map.objects.select_related(), pk=map_id)
	best_runs = BestRun.objects.filter(map=map_obj) \
		.exclude(user__is_active=False).order_by('run__time').extra(
		select = {'position':
			"SELECT COUNT(*)+1 FROM race_bestrun s "
			"WHERE s.map_id = race_bestrun.map_id AND s.time < race_bestrun.time"
		},
	)
	extra_context = {
		'map': map_obj,
	}
	return object_list(request, queryset=best_runs,
		template_name='race/ranks_map_detail.html', extra_context=extra_context)


def map_list(request, map_type=None):
	maps = Map.objects.all().select_related()
	filtered_type = None
	if map_type:
		filtered_type = get_object_or_404(MapType, slug=map_type)
		maps = maps.filter(map_type__slug=map_type)
	map_types = MapType.objects.all()
	extra_context = {
		'map_types': map_types,
		'filtered_type': filtered_type,
	}
	return object_list(request, queryset=maps,
		extra_context=extra_context)


@render_to('race/map_detail.html')
def map_detail(request, map_id):
	map_obj = get_object_or_404(Map.objects.select_related(), pk=map_id)
	best_runs = BestRun.objects.filter(map=map_obj).order_by('run__time').extra(
		select = {'position':
			"SELECT COUNT(*)+1 FROM race_bestrun s "
			"WHERE s.map_id = race_bestrun.map_id AND s.time < race_bestrun.time"
		},
	)[:5]
	latest_runs = Run.objects.filter(map=map_obj).order_by('-created_at')[:5]
	if request.user.is_authenticated():
		user_runs = Run.objects.filter(user=request.user).filter(map=map_obj) \
			.order_by('-created_at')[:5]
	else:
		user_runs = None
	return {
		'map': map_obj,
		'best_runs': best_runs,
		'latest_runs': latest_runs,
		'user_runs': user_runs,
	}


@login_required
def user_activity(request):
	latest_runs = Run.objects.filter(user=request.user).order_by('-created_at')
	return object_list(request, queryset=latest_runs,
		template_name='race/user_activity.html')


@render_to('race/awards.html')
def awards(request):
	"""
	magic.

	yes, you will hate me for this one.
	"""
	award_names = [x for x in dir(badges) if x.endswith('Badge')]
	award_list = []
	for award in award_names:
		award_list.append(getattr(badges, award))
	return {
		'award_list': award_list
	}


def map_download(request, map_id):
	map_obj = get_object_or_404(Map, pk=map_id)
	map_obj.download_count += 1
	map_obj.save()
	return redirect(map_obj.get_download_url())


@render_to('race/live_stats.html')
def live_stats(request):
	servers_online = Server.objects.filter(
		last_connection_at__gte=(datetime.now()-timedelta(minutes=10))
	)
	players_online = UserProfile.objects.filter(
		last_connection_at__gte=(datetime.now()-timedelta(minutes=10))
	)
	# TODO graph?
	return {
		'servers_online': servers_online,
		'players_online': players_online,
	}
