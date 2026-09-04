from django.apps import AppConfig

# Configures the application metadata for the outcomes app
class OutcomesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'outcomes'
    verbose_name = 'Field Atlas Outcomes'
