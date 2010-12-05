from django.conf.urls.defaults import (patterns, url, include,
	handler404, handler500)

# FIXME add 404/500 handlers
# handler404 = ''
# handler500 = ''

urlpatterns = patterns('',
	url(r'^$', 'django.views.generic.simple.direct_to_template',
		{'template': 'home.html'}, name='home'),
	(r'^user/', include('accounts.urls')),
)
