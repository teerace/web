from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('accounts.views',
	(r'^$', 'welcome'),
	url(r'^login/$', 'login', name='login'),
	url(r'^logout/$', 'logout', name='logout'),
	url(r'^register/$', 'register', name='register'),
	(r'^tour/$', 'first_login'),
) + patterns('django.contrib.auth.views',
	(r'^password_reset/$', 'password_reset', {'template_name':
		'accounts/password_reset.html',
		'email_template_name': 'accounts/email/password_reset.html'}),
	(r'^password_reset/done/$', 'password_reset_done', {'template_name':
		'accounts/password_reset_done.html'}),
	(r'^password_reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
		'password_reset_confirm', {'template_name':
		'accounts/password_reset_confirm.html'}),
	(r'^password_reset/complete/$', 'password_reset_complete',
		{'template_name': 'accounts/password_reset_complete.html'}),
)