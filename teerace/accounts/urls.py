from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('accounts.views',
	url(r'^user/$', 'welcome', name='welcome'),
	url(r'^login/$', 'login', name='login'),
	url(r'^logout/$', 'logout', name='logout'),
	url(r'^register/$', 'register', name='register'),
	url(r'^users/$', 'userlist', name='userlist'),
	url(r'^settings/$', 'settings', name='settings'),
	url(r'^getstarted/$', 'first_steps', name='first_steps'),
	url(r'^profile/(?P<user_id>\d+)/$', 'profile', name='profile'),
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
