from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list_detail import object_list
from accounts import badges as account_badges
from accounts.models import UserProfile
from beta import badges as beta_badges
from race.models import Map, MapType, Run, BestRun, Server
from race import badges as race_badges
from annoying.decorators import render_to
from annoying.functions import get_object_or_None


def ranks(request):
	# exclude banned users from rank
	# (that user shouldn't have any points anyway, just a precaution)
	users = UserProfile.objects.filter(points__gt=0) \
		.exclude(user__is_active=False).extra(
		select = {'sql_position':
			"SELECT COUNT(*)+1 FROM accounts_userprofile s "
			"WHERE s.points > accounts_userprofile.points"
		},
		order_by = ['sql_position']
	)
	total_runtime = Run.objects.aggregate(Sum('time'))['time__sum']
	total_runs = Run.objects.count()
	extra_context = {
		'total_runtime': total_runtime,
		'total_runs': total_runs,
	}
	return object_list(request, queryset=users, template_name='race/ranks.html',
		extra_context=extra_context)


def ranks_map_list(request):
	maps = Map.objects.order_by('name').select_related()
	return object_list(request, queryset=maps,
		template_name='race/ranks_map_list.html')


# actually, it's a list of records of a particular map
def ranks_map_detail(request, map_id):
	map_obj = get_object_or_404(Map.objects.select_related(), pk=map_id)
	best_runs = BestRun.objects.filter(map=map_obj) \
		.exclude(user__is_active=False).extra(
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
	maps = maps.order_by('name')
	map_types = MapType.objects.all()
	extra_context = {
		'map_types': map_types,
		'filtered_type': filtered_type,
	}
	return object_list(request, queryset=maps,
		extra_context=extra_context)


@login_required
@render_to('race/map_list_unfinished.html')
def map_list_unfinished(request):
	map_ids = BestRun.objects.filter(user=request.user) \
		.values_list('map_id', flat=True)
	maps = Map.objects.exclude(id__in=map_ids).select_related()
	return {
		'map_types': MapType.objects.all(),
		'maps': maps,
	}


@render_to('race/map_detail.html')
def map_detail(request, map_id):
	map_obj = get_object_or_404(Map.objects.select_related(), pk=map_id)
	best_runs = BestRun.objects.filter(map=map_obj).extra(
		select = {'position':
			"SELECT COUNT(*)+1 FROM race_bestrun s "
			"WHERE s.map_id = race_bestrun.map_id AND s.time < race_bestrun.time"
		},
	)[:5]
	latest_runs = Run.objects.filter(map=map_obj).order_by('-created_at')[:5]
	if request.user.is_authenticated():
		user_latest_runs = Run.objects.filter(user=request.user, map=map_obj) \
			.order_by('-created_at')[:5]
	else:
		user_latest_runs = None
	user_bestrun = get_object_or_None(BestRun, user=request.user, map=map_obj)
	return {
		'map': map_obj,
		'best_runs': best_runs,
		'latest_runs': latest_runs,
		'user_latest_runs': user_latest_runs,
		'user_bestrun': user_bestrun,
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
	award_list = []
	for badges in [race_badges, account_badges, beta_badges]:
		award_names = [x for x in dir(badges) if x.endswith('Badge')]
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


@render_to('race/servers.html')
def servers(request):
	servers_online = Server.objects.filter(
		last_connection_at__gte=(datetime.now()-timedelta(minutes=10))
	)
	players_online_count = UserProfile.objects.filter(
		last_connection_at__gte=(datetime.now()-timedelta(minutes=10))
	).filter(last_played_server__isnull=False).count()
	# TODO graph?
	return {
		'servers_online': servers_online,
		'players_online_count': players_online_count,
	}
