from django.conf.urls import url

from stats.views import chart_list, chart_list_json


urlpatterns = (
    url(r"^$", chart_list, name="chart_list"),
    url(r"^chart_list.json$", chart_list_json, name="chart_list_json"),
)
