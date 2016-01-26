from django.conf.urls import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.views.static import serve
from home.views import homepage
import settings

admin.autodiscover()

urlpatterns = [
	url(r'^$', homepage, name='home'),
	url(r'^api/', include('api.urls')),
	url(r'^blog/', include('blog.urls')),
	url(r'^stats/', include('stats.urls')),
	url(r'^', include('accounts.urls')),
	url(r'^', include('race.urls')),
	url(r'^', include('home.urls')),
	url(r'^c/', include('django_comments.urls')),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^help/', include('faq.urls.shallow')),
	# url(r'^stream/', include('actstream.urls')),
	url(r'^admin/', include(admin.site.urls)),
] + [
	url(r'^about/', TemplateView.as_view(template_name='static/about.html'), name='about'),
	url(r'^contact/', TemplateView.as_view(template_name='static/contact.html'), name='contact'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
	urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

if settings.BETA:
	urlpatterns += [
		url(r'^beta/', include('beta.urls')),
	]