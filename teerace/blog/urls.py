from django.conf.urls.defaults import patterns, url
from blog.feeds import LatestEntriesFeed

urlpatterns = patterns('blog.views',
	url(r'^$', 'entry_list', name='blog'),
	url(r'^entry/(?P<entry_id>\d+)/$', 'entry_detail', name='blog_entry'),
	url(r'^feed/$', LatestEntriesFeed(), name='blog_feed'),
)