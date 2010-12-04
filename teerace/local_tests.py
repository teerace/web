from django.test.simple import run_tests as default_run_tests 
from django.conf import settings 


def run_tests(test_labels, *args, **kwargs): 
	return default_run_tests(settings.OUR_APPS, *args, **kwargs)
