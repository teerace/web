from django.conf.urls import url

from .feeds import LatestEntriesFeed, LatestEntriesForPlanetFeed
from .views import entry_detail, entry_list


urlpatterns = (
    url(r"^$", entry_list, name="blog"),
    url(
        r"^entry/(?P<entry_id>\d+)/(?P<slug>[-\w]+)/$", entry_detail, name="blog_entry"
    ),
    url(r"^entry/(?P<entry_id>\d+)/$", entry_detail, name="blog_entry"),
    url(r"^feed/planet/$", LatestEntriesForPlanetFeed(), name="blog_feed_planet"),
    url(r"^feed/$", LatestEntriesFeed(), name="blog_feed"),
)
