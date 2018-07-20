from django.apps import AppConfig


class DjangoContribAuthConfig(AppConfig):
    name = "django.contrib.auth"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("User"))


class PinaxBadgesConfig(AppConfig):
    name = "pinax.badges"
    label = "brabeion"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("BadgeAward"))
