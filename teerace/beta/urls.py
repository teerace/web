from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('beta.views',
	url(r'^$', 'beta_form', name='beta_form'),
	url(r'^moar_keys/$', 'moar_keys', name='beta_moar_keys'),
)
