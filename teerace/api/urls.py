from django.conf.urls.defaults import patterns, url
from piston.resource import Resource
from api.handlers import RunHandler, UserHandler
from lib.piston_auth import APIKeyAuthentication

auth = APIKeyAuthentication(realm="Teerace")
run_resource = Resource(RunHandler, authentication=auth)
user_resource = RunHandler(UserHandler, authentication=auth)

# 1st revision of API
urlpatterns = patterns('',
	url(r'^1/runs/(?P<id>\d+)/$', run_resource),
	url(r'^1/runs/$', run_resource),
	url(r'^1/users/(?P<id>\d+)/$', user_resource),
	url(r'^1/users/$', user_resource),
)