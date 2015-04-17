from django.conf.urls import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
import settings

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'home.views.homepage', name='home'),
	(r'^api/', include('api.urls')),
	(r'^blog/', include('blog.urls')),
	(r'^stats/', include('stats.urls')),
	(r'^', include('accounts.urls')),
	(r'^', include('race.urls')),
	(r'^', include('home.urls')),
	(r'^c/', include('django_comments.urls')),
	(r'^admin_tools/', include('admin_tools.urls')),
	(r'^help/', include('faq.urls.shallow')),
	# (r'^stream/', include('actstream.urls')),
	(r'^admin/', include(admin.site.urls)),
) + patterns('django.views.generic.simple',
	url(r'^about/', TemplateView.as_view(template_name='static/about.html'), name='about'),
	url(r'^contact/', TemplateView.as_view(template_name='static/contact.html'), name='contact'),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT}),
	)

if settings.BETA:
	urlpatterns += patterns('',
		(r'^beta/', include('beta.urls')),
	)