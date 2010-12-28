from django.conf.urls.defaults import patterns, url
from piston.doc import documentation_view
from api.handlers import RunHandler, UserHandler
from lib.piston_utils import APIKeyAuthentication
from lib.piston_utils import Resource

auth = APIKeyAuthentication(realm="Teerace")
run_resource = Resource(RunHandler, authentication=auth)
user_resource = Resource(UserHandler, authentication=auth)

# 1st revision of API
urlpatterns = patterns('',
	url(r'^1/runs/show/(?P<id>\d+)/$', run_resource,
		name='api_run_manage'),
	url(r'^1/runs/best/(?P<map_name>\w+)/$', run_resource,
		name='api_run_manage'),
	url(r'^1/runs/new/$', run_resource, name='api_run_manage'),
	url(r'^1/users/validate/$', user_resource,
		name='api_user_validate'),
	url(r'^1/users/(?P<id>\d+)/$', user_resource,
		name='api_user_validate'),
	# automated documentation
	url(r'^1/docs/$', documentation_view),
)
