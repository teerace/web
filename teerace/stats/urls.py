from django.conf.urls import *

urlpatterns = patterns('stats.views',
	url(r'^$', 'chart_list', name='chart_list'),
	url(r'^chart_list.json$', 'chart_list_json', name='chart_list_json'),
)
