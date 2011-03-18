from django.conf.urls.defaults import patterns, url
from piston.doc import documentation_view
from api.handlers import RunHandler, UserHandler, MapHandler, PingHandler
from lib.piston_utils import APIKeyAuthentication
from lib.piston_utils import Resource

auth = APIKeyAuthentication(realm="Teerace")
run_resource = Resource(RunHandler, authentication=auth)
user_resource = Resource(UserHandler, authentication=auth)
map_resource = Resource(MapHandler, authentication=auth)
ping_resource = Resource(PingHandler, authentication=auth)

# 1st revision of API
urlpatterns = patterns('',
	url(r'^1/runs/detail/(?P<id>\d+)/$', run_resource, {'action': 'detail'},
		name='api_runs_detail'),
	url(r'^1/runs/(?P<action>\w+)/(?P<id>\d+)/$', run_resource, name='api_runs'),
	url(r'^1/runs/(?P<action>\w+)/$', run_resource, name='api_runs'),
	url(r'^1/users/detail/(?P<id>\d+)/$', user_resource, {'action': 'detail'},
		name='api_users_detail'),
	url(r'^1/users/(?P<action>\w+)/(?P<id>\d+)/(?P<map_id>\d+)/$',
		user_resource, name='api_users'),
	url(r'^1/users/(?P<action>\w+)/(?P<id>\d+)/$', user_resource,
		name='api_users'),
	url(r'^1/users/(?P<action>\w+)/$', user_resource, name='api_users'),
	url(r'^1/maps/detail/(?P<map_id>\d+)/$', map_resource, {'action': 'detail'},
		name='api_maps_detail'),
	url(r'^1/maps/(?P<action>\w+)/(?P<map_id>\d+)/$', map_resource,
		name='api_maps'),
	url(r'^1/maps/(?P<action>\w+)/$', map_resource, name='api_maps'),
	url(r'^1/ping/$', ping_resource, {'action': 'ping'}, name='api_ping_post'),
	url(r'^1/hello/$', ping_resource, {'action': 'hello'}, name='api_ping'),
	# automated documentation
	url(r'^1/docs/$', documentation_view, name='api_docs'),
)
