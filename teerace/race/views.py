import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list
from accounts.models import UserProfile
from blog.models import Entry
from race.models import Map, Run, BestRun
from annoying.decorators import render_to


def homepage(request):
	try:
		latest_entry = Entry.objects.select_related().latest()
	except Entry.DoesNotExist:
		latest_entry = None

	if request.user.is_authenticated():
		user_runs = Run.objects.filter(user=request.user).order_by('-created_at')[:5]
	else:
		user_runs = None

	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)

	runs_today = Run.objects.filter(created_at__range=
		(datetime.datetime.combine(today, datetime.time.min),
		datetime.datetime.combine(today, datetime.time.max)))
	runs_yesterday = Run.objects.filter(created_at__range=
		(datetime.datetime.combine(yesterday, datetime.time.min),
		datetime.datetime.combine(yesterday, datetime.time.max)))

	total_playtime = Run.objects.aggregate(Sum('time'))['time__sum']

	template = 'home.html'
	extra_context = {
		'latest_entry': latest_entry,
		'users': list(UserProfile.objects.select_related()),
		'maps': list(Map.objects.all()),
		'user_runs': user_runs,
		'run_count': Run.objects.count(),
		'runs_today': runs_today,
		'runs_yesterday': runs_yesterday,
		'total_playtime': total_playtime,
	}
	return direct_to_template(request, template, extra_context)


def ranks(request):
	users = UserProfile.objects.filter(points__gt=0).extra(
		select={'position':
			"SELECT COUNT(*)+1 FROM accounts_userprofile s "
			"WHERE s.points > accounts_userprofile.points"
		}
	).order_by('position')
	total_playtime = Run.objects.aggregate(Sum('time'))['time__sum']
	total_runs = Run.objects.count()
	extra_context = {
		'total_playtime': total_playtime,
		'total_runs': total_runs,
	}
	return object_list(request, queryset=users, template_name='race/ranks.html',
		extra_context=extra_context)


def map_list(request):
	maps = Map.objects.all().select_related()
	return object_list(request, queryset=maps)


@render_to('race/map_detail.html')
def map_detail(request, map_id):
	map_obj = get_object_or_404(Map.objects.select_related(), pk=map_id)
	best_runs = BestRun.objects.filter(map=map_obj).order_by('run__time')[:5]
	latest_runs = Run.objects.filter(map=map_obj).order_by('-created_at')[:5]
	if request.user.is_authenticated():
		user_runs = Run.objects.filter(user=request.user).order_by('-created_at')[:5]
	else:
		user_runs = None
	return {
		'map': map_obj,
		'best_runs': best_runs,
		'latest_runs': latest_runs,
		'user_runs': user_runs,
	}
