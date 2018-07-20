from django.conf.urls import url

from race.views import (
    awards,
    map_detail,
    map_download,
    map_list,
    map_list_unfinished,
    ranks,
    ranks_map_detail,
    ranks_map_list,
    servers,
)


urlpatterns = (
    url(r"^maps/$", map_list, name="maps"),
    url(r"^maps/type:(?P<map_type>[\w-]+)$", map_list, name="maps__type"),
    url(r"^maps/unfinished/$", map_list_unfinished, name="maps_unfinished"),
    url(r"^maps/(?P<map_id>\d+)/$", map_detail, name="map_detail"),
    url(r"^maps/(?P<map_id>\d+)/download/$", map_download, name="map_download"),
    url(r"^ranks/$", ranks, name="ranks"),
    url(r"^ranks/maps/$", ranks_map_list, name="ranks_map_list"),
    url(r"^ranks/maps/(?P<map_id>\d+)/$", ranks_map_detail, name="ranks_map_detail"),
    url(r"^awards/$", awards, name="awards"),
    url(r"^servers/$", servers, name="servers"),
)
