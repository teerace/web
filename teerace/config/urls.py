import django_comments.urls
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

import accounts.urls
import api.urls
import blog.urls
import faq.urls.shallow
import home.urls
import race.urls
import stats.urls
from home.views import homepage


urlpatterns = [
    url(r"^$", homepage, name="home"),
    url(r"^api/", include(api.urls)),
    url(r"^blog/", include(blog.urls)),
    url(r"^stats/", include(stats.urls)),
    url(r"^", include(accounts.urls)),
    url(r"^", include(race.urls)),
    url(r"^", include(home.urls)),
    url(r"^c/", include(django_comments.urls)),
    url(r"^help/", include(faq.urls.shallow)),
    # url(r'^stream/', include('actstream.urls')),
    url(r"^admin/", admin.site.urls),
] + [
    url(
        r"^about/",
        TemplateView.as_view(template_name="static/about.html"),
        name="about",
    ),
    url(
        r"^contact/",
        TemplateView.as_view(template_name="static/contact.html"),
        name="contact",
    ),
]


if settings.DEBUG:
    from django.contrib.staticfiles.views import serve
    from django.views import static

    def serve_media(request, path):
        return static.serve(request, path, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        url(r"^static/(?P<path>.*)", serve),
        url(r"^media/(?P<path>.*)", serve_media),
    ]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
