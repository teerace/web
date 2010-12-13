import datetime
from django.views.generic.simple import direct_to_template
from accounts.models import UserProfile
from blog.models import Entry
from race.models import Map, Run

def homepage(request):
	try:
		latest_entry = Entry.objects.select_related().latest()
	except Entry.DoesNotExist:
		latest_entry = None

	today = datetime.date.today()
	yesterday = today - datetime.timedelta(days=1)

	runs_today = Run.objects.filter(reported_at__range=
		(datetime.datetime.combine(today, datetime.time.min),
		datetime.datetime.combine(today, datetime.time.max)))
	runs_yesterday = Run.objects.filter(reported_at__range=
		(datetime.datetime.combine(yesterday, datetime.time.min),
		datetime.datetime.combine(yesterday, datetime.time.max)))

	template = 'home.html'
	extra_context = {
		'latest_entry': latest_entry,
		'users': UserProfile.objects.all().select_related(),
		'maps': Map.objects.all(),
		'run_count': Run.objects.count(),
		'runs_today': runs_today,
		'runs_yesterday': runs_yesterday,
	}
	return direct_to_template(request, template, extra_context)