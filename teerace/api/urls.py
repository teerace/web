from django.conf.urls.defaults import patterns, url
from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from api.handlers import RunHandler

auth = OAuthAuthentication(realm="Teerace")
run_resource = Resource(RunHandler, authentication=auth)

# 1st revision of API
urlpatterns = patterns('',
	url(r'^1/runs/(?P<id>\d+)/$', run_resource),
	url(r'^1/runs/$', run_resource),
) + patterns('piston.authentication',
	url(r'^oauth/request_token/$','oauth_request_token'),
	url(r'^oauth/authorize/$','oauth_user_auth'),
	url(r'^oauth/access_token/$','oauth_access_token'),
)