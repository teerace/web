from django.conf.urls.defaults import (patterns, url, include,
	handler404, handler500)
from django.contrib import admin
import settings

# FIXME add 404/500 handlers
# handler404 = ''
# handler500 = ''

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'django.views.generic.simple.direct_to_template',
		{'template': 'home.html'}, name='home'),
	(r'^user/', include('accounts.urls')),
	(r'^api/', include('api.urls')),
	url(r'^admin_tools/', include('admin_tools.urls')),
	(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT}),
	)