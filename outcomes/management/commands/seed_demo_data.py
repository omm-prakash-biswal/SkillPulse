from django.core.management.base import BaseCommand
from outcomes.utils import seed_default_demo_data

# Management command to populate the database with Field Atlas demo records
class Command(BaseCommand):
    help = 'Seeds the database with initial Field Atlas demo trainers, trainees, placements, and follow-ups'

    # Executes the demo seeding routine and outputs the result summary
    def handle(self, *args, **options):
        self.stdout.write("Starting Field Atlas demo data seeding...")
        results = seed_default_demo_data()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded: {results['users']} users, {results['trainees']} trainees, "
            f"{results['placements']} placements, {results['follow_ups']} follow-ups, {results['consents']} consents."
        ))
