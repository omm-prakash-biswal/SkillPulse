from django.apps import AppConfig
from django.utils import timezone
from datetime import timedelta
from django.db.utils import OperationalError

class OutcomesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'outcomes'
    verbose_name = 'Field Atlas Outcomes'

    def ready(self):
        """Seed demo user and course data in development mode only.
        This runs when the Django app registry is fully populated.
        """
        if not self.apps.is_installed('outcomes'):
            return
        from .models import CustomUser, Trainee
        from django.conf import settings
        try:
            if settings.DEBUG:
                dummy_user_email = 'demo@skillpulse.com'
                dummy_user_password = 'DemoPass123!'
                dummy_user, created = CustomUser.objects.get_or_create(
                    email=dummy_user_email,
                    defaults={
                        'full_name': 'Demo User',
                        'field_atlas_id': 'FA-DEM-0001',
                        'role': 'trainee',
                        'provider': 'DemoProvider',
                        'district': 'DemoDistrict',
                        'state': 'DemoState',
                        'preferred_language': 'en',
                    }
                )
                if created:
                    dummy_user.set_password(dummy_user_password)
                    dummy_user.save()
                # Ensure a trainee record exists
                Trainee.objects.get_or_create(
                    unified_id='FA-DEM-0001',
                    defaults={'user': dummy_user}
                )
        except OperationalError:
            # Database might not be ready yet (e.g., migrations pending)
            pass
