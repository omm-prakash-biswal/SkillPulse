import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP, AuditLog, CustomUser, Trainee, TraineeConsent, Placement, FollowUp

# Generates a pseudo-random 6-digit numeric OTP code
def generate_six_digit_otp():
    return f"{random.randint(100000, 999999)}"


# Creates and dispatches a 6-digit email OTP valid for 10 minutes
def send_email_otp(email, purpose='registration'):
    code = generate_six_digit_otp()
    expires_at = timezone.now() + timedelta(minutes=10)

    # Invalidate existing unverified OTPs for the same purpose
    EmailOTP.objects.filter(email=email, purpose=purpose, is_verified=False).delete()

    otp_obj = EmailOTP.objects.create(
        email=email,
        otp_code=code,
        expires_at=expires_at,
        purpose=purpose
    )

    subject = f"Your Field Atlas Verification Code: {code}"
    message = (
        f"Greetings,\n\n"
        f"Your verification code for Field Atlas ({purpose.replace('_', ' ').title()}) is: {code}\n\n"
        f"This code will expire in 10 minutes. If you did not request this, please disregard this email.\n\n"
        f"— Field Atlas Governance Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
    except Exception as e:
        print(f"[Field Atlas Email Service] Fallback notice: OTP for {email} is {code}. Reason: {e}")

    return otp_obj


# Validates a submitted 6-digit OTP against expiration, attempt limits, and verification status
def verify_email_otp(email, code, purpose='registration'):
    otp_record = EmailOTP.objects.filter(
        email=email,
        purpose=purpose,
        is_verified=False
    ).order_by('-created_at').first()

    if not otp_record:
        return False, "No active verification code found for this email."

    if timezone.now() > otp_record.expires_at:
        return False, "Verification code has expired. Please request a new one."

    if otp_record.attempts >= 3:
        return False, "Maximum verification attempts exceeded. Please request a fresh code."

    if otp_record.otp_code != str(code).strip():
        otp_record.record_failed_attempt()
        remaining = 3 - otp_record.attempts
        return False, f"Incorrect code. {remaining} attempt(s) remaining."

    otp_record.is_verified = True
    otp_record.save()
    return True, "Verification successful."


# Records an entry in the system audit log for security and compliance
def log_audit_event(user, action, target_type, target_id, metadata=None):
    try:
        AuditLog.objects.create(
            user=user if getattr(user, 'is_authenticated', False) else None,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            metadata=metadata or {}
        )
    except Exception as e:
        print(f"[AuditLog Error] Failed to log audit event: {e}")


# Seeds the database with standard Field Atlas demo accounts, trainees, placements, and follow-ups
def seed_default_demo_data():
    results = {'users': 0, 'trainees': 0, 'placements': 0, 'follow_ups': 0, 'consents': 0}

    # 1. Create or retrieve Admin user
    admin_user, created = CustomUser.objects.get_or_create(
        email='admin@fieldatlas.in',
        defaults={
            'full_name': 'Field Atlas Administrator',
            'field_atlas_id': 'FA-AD-0001',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'provider': 'National Skills Operations',
            'district': 'New Delhi',
            'state': 'Delhi'
        }
    )
    if created:
        admin_user.set_password('Atlas@2026!')
        admin_user.save()
        results['users'] += 1

    # 2. Create or retrieve Trainer user
    trainer_user, created = CustomUser.objects.get_or_create(
        email='trainer@fieldatlas.in',
        defaults={
            'full_name': 'Vikram Shinde',
            'field_atlas_id': 'FA-TR-1001',
            'role': 'trainer',
            'phone_number': '+91 98230 11223',
            'provider': 'Saksham Foundation',
            'district': 'Pune',
            'state': 'Maharashtra',
            'bio': 'Lead vocational mentor with 8+ years experience in green energy and digital skills.'
        }
    )
    if created:
        trainer_user.set_password('Atlas@2026!')
        trainer_user.save()
        results['users'] += 1

    # 3. Create or retrieve Trainee user (Asha Devi)
    trainee_user, created = CustomUser.objects.get_or_create(
        email='trainee@fieldatlas.in',
        defaults={
            'full_name': 'Asha Devi',
            'field_atlas_id': 'FA-24-0182',
            'role': 'trainee',
            'phone_number': '+91 94220 88712',
            'provider': 'Saksham Foundation',
            'district': 'Pune',
            'state': 'Maharashtra'
        }
    )
    if created:
        trainee_user.set_password('Atlas@2026!')
        trainee_user.save()
        results['users'] += 1

    # Trainee Specifications from Prompt
    trainees_spec = [
        {
            'unified_id': 'FA-24-0182',
            'name': 'Asha Devi',
            'course': 'Solar PV Installer',
            'provider': 'Saksham',
            'district': 'Pune',
            'state': 'Maharashtra',
            'gender': 'female',
            'age_band': '21-25',
            'stage': 'retained',
            'consent_status': 'active',
            'user': trainee_user,
            'placement': {
                'employer_name': 'Surya Power Solutions',
                'role': 'Field Technician',
                'employment_type': 'formal',
                'wage': 18500.00,
                'source': 'employer_confirmed',
                'validation_status': 'verified',
            },
            'follow_up': {
                'milestone': 'month_12',
                'channel': 'whatsapp',
                'status': 'queued',
                'attempts': 2,
                'notes': '2 attempts completed. Highly cooperative learner.'
            }
        },
        {
            'unified_id': 'FA-24-0224',
            'name': 'Ravi Kumar',
            'course': 'Healthcare Assistant',
            'provider': 'Jan Disha',
            'district': 'Ranchi',
            'state': 'Jharkhand',
            'gender': 'male',
            'age_band': '18-24',
            'stage': 'placed',
            'consent_status': 'active',
            'user': None,
            'placement': {
                'employer_name': 'Apex Diagnostic Centre',
                'role': 'Ward Assistant',
                'employment_type': 'formal',
                'wage': 15000.00,
                'source': 'self_reported',
                'validation_status': 'pending',
            },
            'follow_up': {
                'milestone': 'month_3',
                'channel': 'sms',
                'status': 'queued',
                'attempts': 1,
                'notes': 'No answer on first call today. Reschedule call.'
            }
        },
        {
            'unified_id': 'FA-24-0198',
            'name': 'Meena Kumari',
            'course': 'Tailoring & Design',
            'provider': 'Udaan',
            'district': 'Jaipur',
            'state': 'Rajasthan',
            'gender': 'female',
            'age_band': '25-30',
            'stage': 'certified',
            'consent_status': 'active',
            'user': None,
            'placement': {
                'employer_name': 'Self-Employed Boutique',
                'role': 'Master Tailor',
                'employment_type': 'self_employed',
                'wage': None,
                'source': 'self_reported',
                'validation_status': 'unverified',
            },
            'follow_up': {
                'milestone': 'month_6',
                'channel': 'whatsapp',
                'status': 'needs_assistance',
                'attempts': 1,
                'notes': 'Requested local language assistance for micro-enterprise loan application.'
            }
        },
        {
            'unified_id': 'FA-24-0210',
            'name': 'Javed Ansari',
            'course': 'Electrician',
            'provider': 'Navjeevan',
            'district': 'Guwahati',
            'state': 'Assam',
            'gender': 'male',
            'age_band': '22-26',
            'stage': 'follow_up_due',
            'consent_status': 'active',
            'user': None,
            'placement': {
                'employer_name': 'Brahmaputra Infrastructure',
                'role': 'Junior Electrician',
                'employment_type': 'formal',
                'wage': 16200.00,
                'source': 'employer_confirmed',
                'validation_status': 'verified',
            },
            'follow_up': {
                'milestone': 'month_3',
                'channel': 'whatsapp',
                'status': 'queued',
                'attempts': 0,
                'notes': 'Due Sep 08. Scheduled for check-in.'
            }
        },
        {
            'unified_id': 'FA-24-0241',
            'name': 'Sonal Patil',
            'course': 'Data Entry & GST',
            'provider': 'Saksham',
            'district': 'Pune',
            'state': 'Maharashtra',
            'gender': 'female',
            'age_band': '19-23',
            'stage': 'retained',
            'consent_status': 'active',
            'user': None,
            'placement': {
                'employer_name': 'Zenith Accounting Services',
                'role': 'Accounts Executive',
                'employment_type': 'formal',
                'wage': 21000.00,
                'source': 'employer_confirmed',
                'validation_status': 'verified',
            },
            'follow_up': {
                'milestone': 'month_12',
                'channel': 'assisted',
                'status': 'responded',
                'attempts': 3,
                'notes': 'Completed 12-month retention successfully with salary increment.'
            }
        }
    ]

    for item in trainees_spec:
        trainee, created = Trainee.objects.get_or_create(
            unified_id=item['unified_id'],
            defaults={
                'name': item['name'],
                'course': item['course'],
                'provider': item['provider'],
                'district': item['district'],
                'state': item['state'],
                'gender': item['gender'],
                'age_band': item['age_band'],
                'stage': item['stage'],
                'consent_status': item['consent_status'],
                'assigned_trainer': trainer_user,
                'user': item['user']
            }
        )
        if created:
            results['trainees'] += 1

        # Consent record
        consent, c_created = TraineeConsent.objects.get_or_create(
            trainee=trainee,
            consent_version='v1.0',
            defaults={
                'status': 'granted',
                'source': 'portal_opt_in',
                'consented_at': timezone.now()
            }
        )
        if c_created:
            results['consents'] += 1

        # Placement record
        p_info = item['placement']
        placement, p_created = Placement.objects.get_or_create(
            trainee=trainee,
            employer_name=p_info['employer_name'],
            defaults={
                'role': p_info['role'],
                'employment_type': p_info['employment_type'],
                'wage': p_info['wage'],
                'source': p_info['source'],
                'validation_status': p_info['validation_status'],
                'start_date': timezone.now().date() - timedelta(days=90)
            }
        )
        if p_created:
            results['placements'] += 1

        # FollowUp record
        f_info = item['follow_up']
        follow_up, f_created = FollowUp.objects.get_or_create(
            trainee=trainee,
            milestone=f_info['milestone'],
            defaults={
                'channel': f_info['channel'],
                'status': f_info['status'],
                'attempts': f_info['attempts'],
                'notes': f_info['notes'],
                'due_at': timezone.now(),
                'last_attempt_at': timezone.now() if f_info['attempts'] > 0 else None
            }
        )
        if f_created:
            results['follow_ups'] += 1

    return results
