from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json as simplejson
from stats.models import Chart
from annoying.decorators import render_to


@render_to('stats/chart_list.html')
def chart_list(request):
	return {

	}


def chart_list_json(request):
	charts = Chart.objects.all()
	data = []
	for chart in charts:
		data.append((chart.slug, chart.displayed_name, chart.data))
	response_data = simplejson.dumps(
		data,
		cls=DjangoJSONEncoder,
	)
	return HttpResponse(response_data, content_type="application/json")