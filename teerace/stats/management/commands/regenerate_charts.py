from datetime import date, datetime, time, timedelta
import sys
from django.core.management.base import BaseCommand
from race.models import Run
from stats.models import Chart


class Command(BaseCommand):
	help = ("Rebuilds chart data.")

	def handle(self, *args, **options):
		yesterday = date.today() - timedelta(days=1)
		daily_chart, created = Chart.objects.get_or_create(slug='races-daily')
		overall_chart, created = Chart.objects \
			.get_or_create(slug='races-overall')
		self.stdout.write("Rebuilding charts...\n")
		try:
			first_run_date = Run.objects.order_by('created_at')[0].created_at
			first_run_date = date(first_run_date.year, first_run_date.month,
				first_run_date.day)
		except IndexError:
			self.stdout.write("\nNo Run objects. Aborting.\n")
			sys.exit(1)
		days_number = (yesterday - first_run_date).days + 1
		daily_data = []
		overall_data = []
		for i in xrange(days_number):
			that_day = first_run_date+timedelta(days=i)
			runs_that_day = Run.objects.filter(created_at__range=
				(datetime.combine(that_day, time.min),
				datetime.combine(that_day, time.max))).count()
			runs_to_that_day = Run.objects.filter(created_at__lte=
				that_day).count()
			daily_data.append((that_day, runs_that_day))
			overall_data.append((that_day, runs_to_that_day))
		daily_chart.data = daily_data
		daily_chart.save()
		overall_chart.data = overall_data
		overall_chart.save()
		self.stdout.write("Successfully rebuilt chart data.\n")
		sys.exit(0)
