import os
import uuid
import secrets
import hmac
import hashlib
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .models import (
    EmailOTP, AuditLog, CustomUser, Trainee, TraineeConsent, Placement, FollowUp,
    Course, CourseApplication, Enrollment, Certificate, TraineeOutcome, Notification
)

logger = logging.getLogger('field_atlas')

# Normalizes provider names to canonical casing and naming standards
def normalize_provider_name(name):
    if not name:
        return ''
    cleaned = ' '.join(name.strip().split())
    low = cleaned.lower()
    if 'saksham' in low:
        return 'Saksham'
    if 'jan disha' in low or 'jandisha' in low:
        return 'Jan Disha'
    if 'udaan' in low:
        return 'Udaan'
    if 'navjeevan' in low:
        return 'Navjeevan'
    return cleaned


# Generates a cryptographically secure 6-digit numeric OTP code using secrets
def generate_six_digit_otp():
    return f"{secrets.randbelow(900000) + 100000}"


# Computes an HMAC-SHA256 digest of an OTP string using the application secret key
def hash_otp_code(code):
    key = settings.SECRET_KEY.encode('utf-8')
    msg = str(code).strip().encode('utf-8')
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


# Performs constant-time comparison between a submitted OTP and a stored digest
def verify_otp_digest(code, digest):
    if not digest or not code:
        return False
    computed = hash_otp_code(code)
    return hmac.compare_digest(computed, digest)


# Verifies anti-abuse rate limits for OTP generation based on email and IP address
def check_otp_rate_limit(email, ip_address=None):
    now = timezone.now()

    # 1. 60-second cooldown per email
    recent = EmailOTP.objects.filter(email=email, created_at__gte=now - timedelta(seconds=60)).first()
    if recent:
        return False, "Please wait 60 seconds before requesting another code."

    # 2. Hourly limit: max 5 requests per hour per email
    hourly_email_count = EmailOTP.objects.filter(email=email, created_at__gte=now - timedelta(hours=1)).count()
    if hourly_email_count >= 5:
        return False, "Hourly verification code limit reached for this email. Please try again later."

    # 3. Hourly limit: max 10 requests per hour per IP address
    if ip_address:
        hourly_ip_count = EmailOTP.objects.filter(ip_address=ip_address, created_at__gte=now - timedelta(hours=1)).count()
        if hourly_ip_count >= 10:
            return False, "Too many verification requests from this IP address. Please try again later."

    return True, None


# Generates, hashes, and dispatches a 6-digit email OTP valid for 10 minutes
def send_email_otp(email, purpose='registration', ip_address=None):
    allowed, rate_msg = check_otp_rate_limit(email, ip_address=ip_address)
    if not allowed:
        return False, rate_msg, None

    code = generate_six_digit_otp()
    otp_hash = hash_otp_code(code)
    expires_at = timezone.now() + timedelta(minutes=10)

    # Invalidate existing unverified OTPs for the same purpose
    EmailOTP.objects.filter(email=email, purpose=purpose, is_verified=False).delete()

    otp_obj = EmailOTP.objects.create(
        email=email,
        otp_hash=otp_hash,
        otp_code='',  # Raw code is never stored in plain text
        ip_address=ip_address,
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
        logger.error(f"Email dispatch failed for {email}: {e}")
        if settings.DEBUG:
            logger.info(f"[DEV CONSOLE OTP] Verification code for {email} is: {code}")

    if settings.DEBUG:
        print(f"[Field Atlas Development OTP] Email: {email} | Code: {code}")

    # Log audit event for OTP request
    log_audit_event(None, 'otp_requested', 'EmailOTP', otp_obj.id, {'email': email, 'purpose': purpose, 'ip': ip_address})
    return True, f"Verification code dispatched to {email}. Valid for 10 minutes.", code


# Validates a submitted 6-digit OTP against expiration, attempt limits, and HMAC integrity
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

    # Compare with HMAC hash or legacy plain code fallback
    is_match = False
    if otp_record.otp_hash:
        is_match = verify_otp_digest(code, otp_record.otp_hash)
    elif otp_record.otp_code:
        is_match = hmac.compare_digest(otp_record.otp_code, str(code).strip())

    if not is_match:
        otp_record.record_failed_attempt()
        remaining = 3 - otp_record.attempts
        log_audit_event(None, 'otp_verification_failed', 'EmailOTP', otp_record.id, {'email': email, 'remaining': remaining})
        return False, f"Incorrect code. {remaining} attempt(s) remaining."

    otp_record.is_verified = True
    otp_record.save(update_fields=['is_verified'])
    log_audit_event(None, 'otp_verified', 'EmailOTP', otp_record.id, {'email': email, 'purpose': purpose})
    return True, "Verification successful."


# Records a failed login attempt and temporarily locks the account after 5 consecutive failures
def record_login_failure(user, ip_address=None):
    if not user:
        log_audit_event(None, 'login_failed_unknown', 'User', 'unknown', {'ip': ip_address})
        return False

    user.failed_login_attempts += 1
    if user.failed_login_attempts >= 5:
        user.locked_until = timezone.now() + timedelta(minutes=15)
        user.save(update_fields=['failed_login_attempts', 'locked_until'])
        log_audit_event(user, 'account_locked', 'User', user.id, {'reason': 'repeated_failed_logins', 'ip': ip_address})
        return True

    user.save(update_fields=['failed_login_attempts'])
    log_audit_event(user, 'login_failed', 'User', user.id, {'failed_attempts': user.failed_login_attempts, 'ip': ip_address})
    return False


# Resets login failure counter upon successful authentication
def record_login_success(user, ip_address=None):
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = timezone.now()
    user.save(update_fields=['failed_login_attempts', 'locked_until', 'last_login'])
    log_audit_event(user, 'login_success', 'User', user.id, {'ip': ip_address})


# Validates uploaded profile photo file size, extension, and Pillow image content
def validate_profile_photo(uploaded_file):
    max_size = 2 * 1024 * 1024  # 2MB
    if uploaded_file.size > max_size:
        return False, "File size exceeds 2 MB limit."

    name_lower = uploaded_file.name.lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if not any(name_lower.endswith(ext) for ext in allowed_extensions):
        return False, "Invalid image format. Allowed: JPG, JPEG, PNG, and WebP."

    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.verify()
        if img.format not in ['JPEG', 'PNG', 'WEBP']:
            return False, "Uploaded file content is not a supported image."
        uploaded_file.seek(0)
    except Exception:
        return False, "Corrupted or invalid image file."

    return True, None


# Scopes trainee querysets strictly by assigned trainer unless user is admin or superuser
def get_scoped_trainees(user, queryset=None):
    if queryset is None:
        queryset = Trainee.objects.all()

    if not user or not user.is_authenticated:
        return queryset.none()

    if user.is_superuser or user.role == 'admin':
        return queryset

    if user.role == 'trainer':
        return queryset.filter(assigned_trainer=user)

    if user.role == 'trainee' and hasattr(user, 'trainee_profile'):
        return queryset.filter(id=user.trainee_profile.id)

    return queryset.none()


# Scopes follow-up querysets strictly by assigned trainer or learner identity
def get_scoped_follow_ups(user, queryset=None):
    if queryset is None:
        queryset = FollowUp.objects.all()

    if not user or not user.is_authenticated:
        return queryset.none()

    if user.is_superuser or user.role == 'admin':
        return queryset

    if user.role == 'trainer':
        return queryset.filter(trainee__assigned_trainer=user)

    if user.role == 'trainee' and hasattr(user, 'trainee_profile'):
        return queryset.filter(trainee=user.trainee_profile)

    return queryset.none()


# Scopes placement querysets strictly by assigned trainer or learner identity
def get_scoped_placements(user, queryset=None):
    if queryset is None:
        queryset = Placement.objects.all()

    if not user or not user.is_authenticated:
        return queryset.none()

    if user.is_superuser or user.role == 'admin':
        return queryset

    if user.role == 'trainer':
        return queryset.filter(trainee__assigned_trainer=user)

    if user.role == 'trainee' and hasattr(user, 'trainee_profile'):
        return queryset.filter(trainee=user.trainee_profile)

    return queryset.none()


# Verifies whether a user has permission to view or modify a specific trainee record
def check_trainee_scope(user, trainee):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.role == 'admin':
        return True
    if user.role == 'trainer' and trainee.assigned_trainer_id == user.id:
        return True
    if user.role == 'trainee' and hasattr(user, 'trainee_profile') and trainee.id == user.trainee_profile.id:
        return True
    return False


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
        logger.error(f"Failed to log audit event: {e}")


# Generates a landscape PDF certificate file using ReportLab and attaches it to the Certificate model instance
def generate_certificate_pdf(certificate):
    cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(cert_dir, exist_ok=True)

    filename = f"{certificate.verification_token}.pdf"
    filepath = os.path.join(cert_dir, filename)

    c = canvas.Canvas(filepath, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Soft off-white canvas background
    c.setFillColor(colors.HexColor('#F8FAFC'))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Primary outer border (Deep Indigo #1E2749)
    c.setStrokeColor(colors.HexColor('#1E2749'))
    c.setLineWidth(4)
    c.rect(24, 24, width - 48, height - 48)

    # Inner decorative border (Field Teal #0E8176)
    c.setStrokeColor(colors.HexColor('#0E8176'))
    c.setLineWidth(1.5)
    c.rect(32, 32, width - 64, height - 64)

    # Gold corner ornamental accents
    c.setStrokeColor(colors.HexColor('#D97706'))
    c.setLineWidth(1)
    c.line(40, 40, 100, 40)
    c.line(40, 40, 40, 100)
    c.line(width - 40, 40, width - 100, 40)
    c.line(width - 40, 40, width - 40, 100)
    c.line(40, height - 40, 100, height - 40)
    c.line(40, height - 40, 40, height - 100)
    c.line(width - 40, height - 40, width - 100, height - 40)
    c.line(width - 40, height - 40, width - 40, height - 100)

    # Header branding
    c.setFillColor(colors.HexColor('#1E2749'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 85, "FIELD ATLAS")

    c.setFillColor(colors.HexColor('#0E8176'))
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, height - 104, "SKILLING OUTCOMES PLATFORM • INDIA")

    # Divider bar
    c.setStrokeColor(colors.HexColor('#CBD5E1'))
    c.setLineWidth(0.8)
    c.line(160, height - 116, width - 160, height - 116)

    # Certificate title
    c.setFillColor(colors.HexColor('#1E2749'))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 150, "CERTIFICATE OF COMPLETION")

    c.setFillColor(colors.HexColor('#64748B'))
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width / 2, height - 176, "This is to certify that")

    # Trainee Name
    trainee_name = certificate.enrollment.trainee.name
    c.setFillColor(colors.HexColor('#0F172A'))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 215, trainee_name)

    # Underline trainee name
    name_width = c.stringWidth(trainee_name, "Helvetica-Bold", 26)
    c.setStrokeColor(colors.HexColor('#0E8176'))
    c.setLineWidth(1.5)
    c.line((width - name_width) / 2 - 20, height - 224, (width + name_width) / 2 + 20, height - 224)

    # Program completion statement
    c.setFillColor(colors.HexColor('#475569'))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 252, "has successfully completed the comprehensive competency program in")

    # Course Title
    course_name = certificate.enrollment.course.title
    c.setFillColor(colors.HexColor('#1E2749'))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 282, course_name)

    # Course Code, Sector, & Duration
    details = f"Course Code: {certificate.enrollment.course.course_code}  |  Category: {certificate.enrollment.course.category}  |  Duration: {certificate.enrollment.course.duration_weeks} Weeks"
    c.setFillColor(colors.HexColor('#64748B'))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 304, details)

    # Training Provider
    provider = certificate.enrollment.course.provider or "Saksham Skill Academy"
    c.setFillColor(colors.HexColor('#334155'))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 326, f"Conducted by: {provider}")

    # Bottom Metadata Divider
    c.setStrokeColor(colors.HexColor('#E2E8F0'))
    c.setLineWidth(1)
    c.line(60, 160, width - 60, 160)

    # Date and Identifier Details (Left)
    issue_date_str = certificate.issued_at.strftime('%d %B %Y') if certificate.issued_at else timezone.now().strftime('%d %B %Y')
    c.setFillColor(colors.HexColor('#475569'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(65, 135, "DATE OF ISSUE:")
    c.setFont("Helvetica", 10)
    c.drawString(160, 135, issue_date_str)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(65, 118, "CERTIFICATE ID:")
    c.setFont("Helvetica", 10)
    c.drawString(160, 118, certificate.certificate_number)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(65, 101, "TRAINEE ID:")
    c.setFont("Helvetica", 10)
    c.drawString(160, 101, certificate.enrollment.trainee.unified_id)

    # Public Verification URL Details (Center)
    c.setFillColor(colors.HexColor('#0E8176'))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width / 2, 125, "ONLINE VERIFICATION")
    c.setFillColor(colors.HexColor('#64748B'))
    c.setFont("Helvetica", 8.5)
    verify_url = f"/certificate/verify/{certificate.verification_token}/"
    c.drawCentredString(width / 2, 110, f"Verify authenticity at: {verify_url}")
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 95, f"Token: {certificate.verification_token}")

    # Instructor Signature (Right)
    trainer_name = certificate.enrollment.course.trainer.get_full_name() or certificate.enrollment.course.trainer.email
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor('#1E2749'))
    c.drawRightString(width - 65, 135, trainer_name)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#64748B'))
    c.drawRightString(width - 65, 120, "Authorized Lead Instructor")
    c.drawRightString(width - 65, 105, "Field Atlas Certification Board")
    c.setStrokeColor(colors.HexColor('#94A3B8'))
    c.setLineWidth(0.8)
    c.line(width - 220, 148, width - 65, 148)

    # Tamper-evidence security notice
    c.setFillColor(colors.HexColor('#94A3B8'))
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(width / 2, 48, "This credential is tamper-evident and digitally logged on the Field Atlas Skilling Outcomes Platform.")

    c.showPage()
    c.save()

    rel_path = f"certificates/{filename}"
    certificate.pdf_file.name = rel_path
    certificate.save(update_fields=['pdf_file'])
    return rel_path


# Creates an in-app user notification and saves it to the database
def create_notification(user, title, message, category='general', sender=None, related_course=None, related_enrollment=None):
    if not user:
        return None
    type_map = {
        'application': 'application',
        'enrollment': 'enrollment',
        'certificate': 'certificate',
        'outcome': 'outcome_reminder',
        'outcome_reminder': 'outcome_reminder',
        'general': 'general'
    }
    notif_type = type_map.get(category, 'general')
    return Notification.objects.create(
        recipient=user,
        sender=sender,
        title=title,
        body=message,
        type=notif_type,
        related_course=related_course,
        related_enrollment=related_enrollment
    )


# Dispatches an employment outcome survey reminder notification to an enrolled trainee
def send_outcome_reminder(enrollment, requesting_user=None):
    trainee = enrollment.trainee
    user = trainee.user
    if not user:
        return False, "Trainee does not have an active user account."

    create_notification(
        user=user,
        title=f"Employment Outcome Survey: {enrollment.course.title}",
        message=f"Hello {trainee.name}, please take a moment to update your post-training employment status and salary details for {enrollment.course.title}.",
        category='outcome_reminder',
        sender=requesting_user,
        related_course=enrollment.course,
        related_enrollment=enrollment
    )
    log_audit_event(
        user=requesting_user,
        action='send_outcome_reminder',
        target_type='Enrollment',
        target_id=enrollment.id,
        metadata={'trainee_id': trainee.id, 'course_id': enrollment.course.id}
    )
    return True, "Reminder dispatched successfully."


# Seeds the database with standard Field Atlas demo accounts, trainees, placements, and follow-ups
def seed_default_demo_data():
    results = {'users': 0, 'trainees': 0, 'placements': 0, 'follow_ups': 0, 'consents': 0, 'courses': 0, 'applications': 0, 'enrollments': 0, 'certificates': 0, 'outcomes': 0, 'notifications': 0}

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
            'provider': 'Saksham',
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
            'provider': 'Saksham',
            'district': 'Pune',
            'state': 'Maharashtra'
        }
    )
    if created:
        trainee_user.set_password('Atlas@2026!')
        trainee_user.save()
        results['users'] += 1

    # Trainee Specifications with normalized canonical provider names
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
                'provider': normalize_provider_name(item['provider']),
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
        elif trainee.assigned_trainer != trainer_user:
            trainee.assigned_trainer = trainer_user
            trainee.save(update_fields=['assigned_trainer'])

        # Safely reuse existing consent record or create new one if none exists without deleting historical duplicates
        consent = TraineeConsent.objects.filter(
            trainee=trainee,
            consent_version='v1.0'
        ).order_by('-created_at', '-id').first()

        if not consent:
            consent = TraineeConsent.objects.create(
                trainee=trainee,
                consent_version='v1.0',
                status='granted',
                source='portal_opt_in',
                consented_at=timezone.now()
            )
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

    # 4. Seed Demo Courses
    courses_data = [
        {
            'course_code': 'CRS-SOLAR-101',
            'title': 'Solar PV Installation & Grid Maintenance',
            'category': 'Renewable Energy',
            'duration_weeks': 12,
            'start_date': timezone.now().date() - timedelta(days=60),
            'end_date': timezone.now().date() + timedelta(days=30),
            'capacity': 30,
            'status': 'published',
            'district': 'Pune',
            'state': 'Maharashtra',
            'description': 'Comprehensive hands-on training on solar PV rooftop installation, inverter configuration, safety earthing, and grid synchronization.',
            'trainer': trainer_user,
            'provider': 'Saksham'
        },
        {
            'course_code': 'CRS-GST-201',
            'title': 'Data Entry & GST Compliance',
            'category': 'Information Technology',
            'duration_weeks': 8,
            'start_date': timezone.now().date() - timedelta(days=20),
            'end_date': timezone.now().date() + timedelta(days=40),
            'capacity': 25,
            'status': 'published',
            'district': 'Pune',
            'state': 'Maharashtra',
            'description': 'Applied computer instruction in TallyPrime, GST filing, invoice reconciliation, ledger management, and data hygiene.',
            'trainer': trainer_user,
            'provider': 'Saksham'
        },
        {
            'course_code': 'CRS-ELEC-301',
            'title': 'Industrial Electrician & Automation Wiring',
            'category': 'Electrical & Electronics',
            'duration_weeks': 16,
            'start_date': timezone.now().date() + timedelta(days=10),
            'end_date': timezone.now().date() + timedelta(days=120),
            'capacity': 20,
            'status': 'draft',
            'district': 'Pune',
            'state': 'Maharashtra',
            'description': 'Advanced industrial wiring, relay logic, safety lockouts, three-phase power distribution, and PLC fundamentals.',
            'trainer': trainer_user,
            'provider': 'Saksham'
        }
    ]

    seeded_courses = {}
    for c_spec in courses_data:
        course, c_created = Course.objects.get_or_create(
            course_code=c_spec['course_code'],
            defaults=c_spec
        )
        seeded_courses[c_spec['course_code']] = course
        if c_created:
            results['courses'] += 1

    # 5. Seed Demo Applications & Enrollments for Asha Devi (unified_id 'FA-24-0182')
    asha_trainee = Trainee.objects.filter(unified_id='FA-24-0182').first()
    if asha_trainee and 'CRS-SOLAR-101' in seeded_courses:
        solar_course = seeded_courses['CRS-SOLAR-101']

        # Course 1 Application (Approved)
        app1, a_created = CourseApplication.objects.get_or_create(
            course=solar_course,
            trainee=asha_trainee,
            defaults={
                'status': 'approved',
                'motivation': 'Eager to build a career in clean energy and support solar electrification in rural Maharashtra.',
                'reviewed_by': trainer_user,
                'trainer_note': 'Applicant meets technical criteria and demonstrated high motivation.',
                'reviewed_at': timezone.now() - timedelta(days=55)
            }
        )
        if a_created:
            results['applications'] += 1

        # Course 1 Enrollment (Completed)
        enroll1, e_created = Enrollment.objects.get_or_create(
            course=solar_course,
            trainee=asha_trainee,
            defaults={
                'application': app1,
                'status': 'completed',
                'completion_percent': 100,
                'completed_at': timezone.now() - timedelta(days=20),
                'completion_notes': 'Graduated with exemplary practical lab marks.',
                'marked_completed_by': trainer_user
            }
        )
        if e_created:
            results['enrollments'] += 1

        # Certificate for Course 1
        cert, cert_created = Certificate.objects.get_or_create(
            enrollment=enroll1,
            defaults={
                'certificate_number': 'FA-CERT-2026-0001',
                'issued_by': trainer_user,
                'status': 'issued'
            }
        )
        if cert_created:
            results['certificates'] += 1
            try:
                generate_certificate_pdf(cert)
            except Exception as e:
                logger.error(f"Failed to generate certificate PDF during seeding: {e}")
        elif not cert.pdf_file:
            try:
                generate_certificate_pdf(cert)
            except Exception as e:
                logger.error(f"Failed to regenerate certificate PDF during seeding: {e}")

        # TraineeOutcome for Course 1
        outcome, o_created = TraineeOutcome.objects.get_or_create(
            enrollment=enroll1,
            defaults={
                'employment_status': 'employed',
                'employer_name': 'Surya Power Solutions',
                'job_role': 'Field Technician',
                'monthly_earning': 18500.00,
                'employment_type': 'Formal Employment',
                'current_district': 'Pune',
                'current_state': 'Maharashtra',
                'response_notes': 'Verified through employer offer letter and salary slip.',
                'verification_status': 'verified',
                'verified_by': trainer_user
            }
        )
        if o_created:
            results['outcomes'] += 1

    if asha_trainee and 'CRS-GST-201' in seeded_courses:
        gst_course = seeded_courses['CRS-GST-201']

        # Course 2 Application (Approved)
        app2, a2_created = CourseApplication.objects.get_or_create(
            course=gst_course,
            trainee=asha_trainee,
            defaults={
                'status': 'approved',
                'motivation': 'Seeking to upgrade accounting skills for billing solar component supplies.',
                'reviewed_by': trainer_user,
                'trainer_note': 'Enrolled in evening batch.',
                'reviewed_at': timezone.now() - timedelta(days=15)
            }
        )
        if a2_created:
            results['applications'] += 1

        # Course 2 Enrollment (Active, 65% progress)
        enroll2, e2_created = Enrollment.objects.get_or_create(
            course=gst_course,
            trainee=asha_trainee,
            defaults={
                'application': app2,
                'status': 'active',
                'completion_percent': 65
            }
        )
        if e2_created:
            results['enrollments'] += 1

    # 6. Seed In-App Notifications
    notifs = [
        {
            'recipient': trainee_user,
            'title': 'Certificate Issued',
            'body': 'Congratulations! Your verifiable certificate for Solar PV Installation & Grid Maintenance is now ready to download.',
            'type': 'certificate',
            'related_course': seeded_courses.get('CRS-SOLAR-101')
        },
        {
            'recipient': trainee_user,
            'title': 'Post-Course Outcome Survey',
            'body': 'Please submit your employment outcome details for Solar PV Installation & Grid Maintenance.',
            'type': 'outcome_reminder',
            'related_course': seeded_courses.get('CRS-SOLAR-101')
        },
        {
            'recipient': trainer_user,
            'title': 'Course Enrollment Milestone',
            'body': 'Asha Devi has reached 100% course completion in Solar PV Installation & Grid Maintenance.',
            'type': 'enrollment',
            'related_course': seeded_courses.get('CRS-SOLAR-101')
        }
    ]

    for n_spec in notifs:
        if n_spec['recipient']:
            notif, n_created = Notification.objects.get_or_create(
                recipient=n_spec['recipient'],
                title=n_spec['title'],
                defaults=n_spec
            )
            if n_created:
                results['notifications'] += 1

    return results
