from django.apps import AppConfig


class RaceConfig(AppConfig):
    name = 'race'

    def ready(self):
    	from actstream import registry
        registry.register(self.get_model('Map'))
