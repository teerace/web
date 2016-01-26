from django.conf.urls import *
from blog.feeds import LatestEntriesFeed, LatestEntriesForPlanetFeed
from blog.views import entry_list, entry_detail

urlpatterns = (
	url(r'^$', entry_list, name='blog'),
	url(r'^entry/(?P<entry_id>\d+)/(?P<slug>[-\w]+)/$', entry_detail,
		name='blog_entry'),
	url(r'^entry/(?P<entry_id>\d+)/$', entry_detail, name='blog_entry'),
	url(r'^feed/planet/$', LatestEntriesForPlanetFeed(), name='blog_feed_planet'),
	url(r'^feed/$', LatestEntriesFeed(), name='blog_feed'),
)