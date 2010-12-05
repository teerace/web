from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
	(r'^$', 'welcome'),
	url(r'^login/$', 'login', name='login'),
	url(r'^logout/$', 'logout', name='logout'),
	url(r'^register/$', 'register', name='register'),
	(r'^tour/$', 'first_login'),
)
