from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('home.views',
	url(r'^stream_since/(?P<timestamp_since>[\d]+)/$',
		'stream_since_json', name='stream_since_json'),
)
