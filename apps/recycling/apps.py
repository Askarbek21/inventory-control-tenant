from django.apps import AppConfig


class RecyclingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.recycling'


    def ready(self):
        import apps.recycling.signals
