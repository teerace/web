from django.apps import AppConfig
from actstream import registry


class RaceConfig(AppConfig):
    name = 'race'

    def ready(self):
        registry.register(self.get_model('Map'))
