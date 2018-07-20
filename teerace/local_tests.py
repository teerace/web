from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner


class LocalTestSuiteRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        test_labels = settings.OUR_APPS
        return super().run_tests(test_labels, extra_tests, **kwargs)
