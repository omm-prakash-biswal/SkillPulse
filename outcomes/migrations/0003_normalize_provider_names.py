from django.db import migrations

# Normalizes existing provider names in Trainee and CustomUser models to canonical standards
def normalize_provider_names(apps, schema_editor):
    Trainee = apps.get_model('outcomes', 'Trainee')
    CustomUser = apps.get_model('outcomes', 'CustomUser')

    canonical_map = {
        'saksham foundation': 'Saksham',
        'saksham': 'Saksham',
        'jan disha': 'Jan Disha',
        'jandisha': 'Jan Disha',
        'udaan': 'Udaan',
        'navjeevan': 'Navjeevan',
    }

    # Normalize Trainee records
    for trainee in Trainee.objects.all():
        if trainee.provider:
            cleaned = ' '.join(trainee.provider.strip().split())
            canonical = canonical_map.get(cleaned.lower(), cleaned)
            if canonical != trainee.provider:
                trainee.provider = canonical
                trainee.save(update_fields=['provider'])

    # Normalize CustomUser records
    for user in CustomUser.objects.all():
        if user.provider:
            cleaned = ' '.join(user.provider.strip().split())
            canonical = canonical_map.get(cleaned.lower(), cleaned)
            if canonical != user.provider:
                user.provider = canonical
                user.save(update_fields=['provider'])


# No-op reverse migration since normalization is non-destructive
def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('outcomes', '0002_customuser_failed_login_attempts_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_provider_names, noop_reverse),
    ]
