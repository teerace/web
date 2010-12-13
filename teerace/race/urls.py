from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('race.views',
	url(r'^maps/$', 'map_list', name='maps'),
	url(r'^maps/(?P<map_id>\d+)/$', 'map_detail', name='map_detail'),
)