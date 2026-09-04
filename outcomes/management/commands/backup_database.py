import os
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from outcomes.models import CustomUser, Trainee, TraineeConsent, Placement, FollowUp, AuditLog

# Management command to generate a timestamped JSON backup snapshot of the Field Atlas database
class Command(BaseCommand):
    help = 'Creates a timestamped JSON backup file of all Field Atlas database tables'

    # Exports all primary database tables into a structured backup archive file
    def handle(self, *args, **options):
        backup_dir = settings.BASE_DIR / 'backups'
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"field_atlas_backup_{timestamp}.json"

        self.stdout.write(f"Starting database backup to {backup_file}...")

        models_to_backup = [CustomUser, Trainee, TraineeConsent, Placement, FollowUp, AuditLog]
        all_objects = []

        for model in models_to_backup:
            queryset = model.objects.all()
            all_objects.extend(list(queryset))

        serialized_data = serializers.serialize('json', all_objects, indent=2)

        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(serialized_data)

        self.stdout.write(self.style.SUCCESS(
            f"Backup complete! Successfully archived {len(all_objects)} records to {backup_file.name}."
        ))
