from django.apps import AppConfig


class EscalationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'escalation'
    
    
    def ready(self) -> None:
        from . import signals