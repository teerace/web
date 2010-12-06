from django.conf.urls.defaults import (patterns, url, include,
	handler404, handler500)
from django.contrib import admin

# DIRTY workaround for http://bitbucket.org/jespern/django-piston/issue/117/
# uncomment or remove while installing django-admin-tools
#from piston.models import Consumer

# FIXME add 404/500 handlers
# handler404 = ''
# handler500 = ''

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'django.views.generic.simple.direct_to_template',
		{'template': 'home.html'}, name='home'),
	(r'^user/', include('accounts.urls')),
	(r'^api/', include('api.urls')),
	(r'^admin/', include(admin.site.urls)),
)
