from django.conf.urls import url

from .views import server_timestamp, stream_since_json


urlpatterns = (
    url(
        r"^stream_since/(?P<since_timestamp>[\d]+)/$",
        stream_since_json,
        name="stream_since_json",
    ),
    url(r"^timestamp/$", server_timestamp, name="server_timestamp"),
)
