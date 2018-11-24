from django.conf.urls import url

from . import views


app_name = "v1"
urlpatterns = [
    url(r"^activity/new/$", views.ActivityCreateView.as_view()),
    url(
        r"^users/detail/(?P<user_id>\d+)/$",
        views.UserDetailView.as_view(),
        name="user_detail",
    ),
    url(r"^users/profile/(?P<user_id>\d+)/$", views.UserProfileDetailView.as_view()),
    url(r"^users/rank/(?P<user_id>\d+)/$", views.UserRankView.as_view()),
    url(
        r"^users/map_rank/(?P<user_id>\d+)/(?P<map_id>\d+)/$",
        views.UserMapRankView.as_view(),
    ),
    url(r"^users/auth_token/$", views.UserAuthTokenView.as_view()),
    url(r"^users/get_by_name/$", views.UserGetByNameView.as_view()),
    url(r"^users/skin/(?P<user_id>\d+)/$", views.UserSkinView.as_view()),
    url(r"^users/playtime/(?P<user_id>\d+)/$", views.UserPlaytimeView.as_view()),
    url(
        r"^runs/detail/(?P<run_id>\d+)/$",
        views.RunDetailView.as_view(),
        name="run_detail",
    ),
    url(r"^runs/new/$", views.RunCreateView.as_view()),
    url(
        r"^files/demo/(?P<user_id>\d+)/(?P<map_id>\d+)/$",
        views.DemoUploadView.as_view(),
    ),
    url(
        r"^files/ghost/(?P<user_id>\d+)/(?P<map_id>\d+)/$",
        views.GhostUploadView.as_view(),
    ),
    url(
        r"^maps/detail/(?P<map_id>\d+)/$",
        views.MapDetailView.as_view(),
        name="map_detail",
    ),
    url(r"^maps/list/$", views.MapListView.as_view()),
    url(r"^maps/list/(?P<type>[\w\s-]+)/$", views.MapListView.as_view()),
    url(r"^maps/rank/(?P<map_id>\d+)/$", views.MapRankView.as_view()),
    url(r"^maps/rank/(?P<map_id>\d+)/(?P<offset>\d+)/$", views.MapRankView.as_view()),
    url(r"^ping/$", views.PingView.as_view()),
    url(r"^hello/$", views.HelloView.as_view()),
    url(r"^anonclient/get_token/$", views.UserTokenView.as_view()),
    url(r"^anonclient/servers/$", views.ServerListView.as_view()),
]
