from django.conf.urls.defaults import patterns, url, include, handler404, handler500
from django.contrib import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'race.views.homepage', name='home'),
	(r'^api/', include('api.urls')),
	(r'^blog/', include('blog.urls')),
	(r'^', include('accounts.urls')),
	(r'^', include('race.urls')),
	(r'^c/', include('django.contrib.comments.urls')),
	(r'^admin_tools/', include('admin_tools.urls')),
	(r'^help/', include('faq.urls.shallow')),
	(r'^admin/', include(admin.site.urls)),
) + patterns('django.views.generic.simple',
	url(r'^about/', 'direct_to_template',
		{'template': 'static/about.html'}, name='about'),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT}),
	)
