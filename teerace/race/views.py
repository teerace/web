from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect
from accounts.models import UserProfile
from race.models import Map, MapType, Run, BestRun, Server
from annoying.decorators import render_to
from annoying.functions import get_object_or_None
from brabeion import badges
from brabeion.models import BadgeAward


@render_to('race/ranks.html')
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
	return {
		'total_runtime': total_runtime,
		'total_runs': total_runs,
		'object_list': users,
	}


@render_to('race/ranks_map_list.html')
def ranks_map_list(request):
	maps = Map.objects.order_by('name').select_related()
	return {
		'object_list': maps,
	}


# actually, it's a list of records of a particular map
@render_to('race/ranks_map_detail.html')
def ranks_map_detail(request, map_id):
	map_obj = get_object_or_404(Map.objects.select_related(), pk=map_id)
	best_runs = BestRun.objects.filter(map=map_obj) \
		.exclude(user__is_active=False).extra(
		select = {'position':
			"SELECT COUNT(*)+1 FROM race_bestrun s "
			"WHERE s.map_id = race_bestrun.map_id AND s.time < race_bestrun.time"
		},
	)
	return{
		'map': map_obj,
		'object_list': best_runs,
	}


@render_to('race/map_list.html')
def map_list(request, map_type=None):
	maps = Map.objects.all().select_related()
	filtered_type = None
	if map_type:
		filtered_type = get_object_or_404(MapType, slug=map_type)
		maps = maps.filter(map_types__slug=map_type)
	maps = maps.order_by('name')
	map_types = MapType.objects.all()
	return {
		'map_types': map_types,
		'filtered_type': filtered_type,
		'object_list': maps,
	}


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
		user_bestrun = get_object_or_None(BestRun, user=request.user,
			map=map_obj)
	else:
		user_latest_runs = None
		user_bestrun = None
	return {
		'map': map_obj,
		'best_runs': best_runs,
		'latest_runs': latest_runs,
		'user_latest_runs': user_latest_runs,
		'user_bestrun': user_bestrun,
	}


@render_to('race/awards.html')
def awards(request):
	if request.user.is_authenticated():
		user_badges = set((slug, level) for slug, level in
			BadgeAward.objects.filter(
				user = request.user
			).values_list("slug", "level"))
	else:
		user_badges = []

	badges_awarded = BadgeAward.objects.values("slug", "level").annotate(
		num = Count("pk")
	)

	badges_counts = {"{0}_{1}".format(k['slug'], k['level']): k['num'] for k in badges_awarded}

	user_count = UserProfile.objects.count()

	badges_list = list()
	for badge_cls in badges._registry.values():
		for level, badge in enumerate(badge_cls.levels):
			badge_count = badges_counts.get("{0}_{1}".format(badge_cls.slug, level), 0)
			badges_list.append({
				"slug": badge_cls.slug,
				"level": level,
				"name": badge.name,
				"description": badge.description,
				"count": badge_count,
				"percentage": badge_count/float(user_count) * 100 if user_count else 0,
				"user_has": (badge_cls.slug, level) in user_badges,
			})

	return {
		'badges_list': badges_list,
		'user_count': user_count,
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
