from django.shortcuts import get_object_or_404
from stats.models import Chart
from annoying.decorators import render_to


@render_to('stats/chart_list.html')
def chart_list(request):
	charts = Chart.objects.all()
	return {
		'charts': charts,
	}