from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings


class LocalTestSuiteRunner(DjangoTestSuiteRunner):

	def run_tests(self, test_labels, extra_tests=None, **kwargs):
		del test_labels
		super(LocalTestSuiteRunner, self).run_tests(settings.OUR_APPS,
			extra_tests, **kwargs)

