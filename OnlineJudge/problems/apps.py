from django.apps import AppConfig

class ProblemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'problems'

    def ready(self):
        import problems.signals  # Register the signal handlers
