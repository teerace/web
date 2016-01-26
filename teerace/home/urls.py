from django.conf.urls import *
from home.views import stream_since_json, server_timestamp

urlpatterns = (
	url(r'^stream_since/(?P<since_timestamp>[\d]+)/$',
		stream_since_json, name='stream_since_json'),
	url(r'^timestamp/$', server_timestamp, name='server_timestamp'),
)
