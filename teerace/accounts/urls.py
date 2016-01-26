from django.conf.urls import *
from accounts.views import *
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

urlpatterns = [
	url(r'^user/$', welcome, name='welcome'),
	url(r'^login/$', login, name='login'),
	url(r'^logout/$', logout, name='logout'),
	url(r'^register/$', register, name='register'),
	url(r'^users/$', userlist, name='userlist'),
	url(r'^settings/$', settings, name='settings'),
	url(r'^settings/password/$', password_change, name='password_change'),
	url(r'^settings/api_token/$', api_token, name='api_token'),
	url(r'^getstarted/$', first_steps, name='first_steps'),
	url(r'^profile/(?P<user_id>\d+)/$', profile, name='profile'),
	url(r'^profile/(?P<user_id>\d+)/points_graph.json$',
		profile_points_graph_json, name='profile_points_graph_json'),
	url(r'^profile/(?P<user_id>\d+)/badges/$', profile_badges,
		name='profile_badges'),
	url(r'^profile/(?P<user_id>\d+)/best/$', profile_best,
		name='profile_best'),
	url(r'^profile/(?P<user_id>\d+)/activity/$', profile_activity,
		name='profile_activity'),
] + [
	url(r'^password_reset/$', password_reset, {'template_name':
		'accounts/password_reset.html',
		'email_template_name': 'accounts/email/password_reset.html'},
		name='password_reset'),
	url(r'^password_reset/done/$', password_reset_done, {'template_name':
		'accounts/password_reset_done.html'},
		name='password_reset_done'),
	url(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
		password_reset_confirm, {'template_name':
		'accounts/password_reset_confirm.html'},
		name='password_reset_confirm'),
	url(r'^password_reset/complete/$', password_reset_complete,
		{'template_name': 'accounts/password_reset_complete.html'},
		name='password_reset_complete'),
]
