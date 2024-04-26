# apps.py
from django.apps import AppConfig

class SeepsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seepsApp'
    
    def ready(self):
        import seepsApp.signals
