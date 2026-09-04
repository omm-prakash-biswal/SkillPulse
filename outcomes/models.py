from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import secrets
import uuid

# Manages user creation and password hashing for CustomUser
class CustomUserManager(BaseUserManager):
    # Creates and saves a standard user with an email and optional Field Atlas ID
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if not extra_fields.get('field_atlas_id'):
            prefix = 'FA-TR' if extra_fields.get('role') == 'trainer' else 'FA-24'
            random_num = secrets.randbelow(9000) + 1000
            extra_fields['field_atlas_id'] = f"{prefix}-{random_num}"
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    # Creates and saves an administrative superuser with full permissions
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


# Custom user model supporting Trainers, Trainees, and Admins with Field Atlas identities
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('trainer', 'Trainer'),
        ('trainee', 'Trainee'),
        ('admin', 'Admin'),
    )

    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('mr', 'Marathi'),
        ('bn', 'Bengali'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('kn', 'Kannada'),
        ('gu', 'Gujarati'),
        ('pa', 'Punjabi'),
        ('ml', 'Malayalam'),
        ('ur', 'Urdu'),
    )

    full_name = models.CharField(max_length=150, verbose_name='Full Name')
    email = models.EmailField(unique=True, verbose_name='Email Address')
    field_atlas_id = models.CharField(max_length=32, unique=True, db_index=True, verbose_name='Field Atlas ID')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='trainer', verbose_name='User Role')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Phone Number')
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en', verbose_name='Preferred Language')
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True, verbose_name='Profile Photo')
    provider = models.CharField(max_length=150, blank=True, verbose_name='Training Provider / Organisation')
    district = models.CharField(max_length=100, blank=True, verbose_name='District')
    state = models.CharField(max_length=100, blank=True, verbose_name='State')
    address = models.TextField(blank=True, verbose_name='Postal Address')
    bio = models.TextField(blank=True, verbose_name='Professional Bio')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff')
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name='Failed Login Attempts')
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name='Account Lockout Expiry')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    # Returns the primary string representation of the user
    def __str__(self):
        return f"{self.full_name} ({self.field_atlas_id}) [{self.role}]"

    # Returns the user's full name
    def get_full_name(self):
        return self.full_name or self.email

    # Returns the user's short or first name
    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email

    # Returns the user display name or falls back to email
    def get_display_name(self):
        return self.full_name or self.email.split('@')[0]

    # Checks if the user has trainer privileges
    def is_trainer_role(self):
        return self.role == 'trainer' or self.is_superuser

    # Checks if the user has trainee privileges
    def is_trainee_role(self):
        return self.role == 'trainee'

    # Checks whether the user account is currently temporarily locked out
    def is_locked_out(self):
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False


# Represents a participant in a skill training programme
class Trainee(models.Model):
    GENDER_CHOICES = (
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer Not to Say'),
    )

    STAGE_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('trained', 'Trained'),
        ('certified', 'Certified'),
        ('placed', 'Placed'),
        ('retained', 'Retained'),
        ('follow_up_due', 'Follow-up Due'),
    )

    CONSENT_CHOICES = (
        ('active', 'Active'),
        ('withdrawn', 'Withdrawn'),
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trainee_profile',
        verbose_name='Associated User Account'
    )
    unified_id = models.CharField(max_length=32, unique=True, db_index=True, verbose_name='Unified ID')
    name = models.CharField(max_length=150, verbose_name='Learner Name')
    course = models.CharField(max_length=150, verbose_name='Course')
    provider = models.CharField(max_length=150, verbose_name='Training Provider')
    district = models.CharField(max_length=100, verbose_name='District')
    state = models.CharField(max_length=100, verbose_name='State')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='prefer_not_to_say', verbose_name='Gender')
    age_band = models.CharField(max_length=30, default='18-24', verbose_name='Age Band')
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='enrolled', verbose_name='Current Stage')
    consent_status = models.CharField(max_length=20, choices=CONSENT_CHOICES, default='active', verbose_name='Consent Status')
    assigned_trainer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_trainees',
        verbose_name='Assigned Trainer'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Trainee'
        verbose_name_plural = 'Trainees'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['unified_id']),
            models.Index(fields=['provider']),
            models.Index(fields=['assigned_trainer']),
            models.Index(fields=['stage']),
            models.Index(fields=['consent_status']),
        ]

    # Returns the readable representation of the trainee
    def __str__(self):
        return f"{self.name} ({self.unified_id}) - {self.course}"

    # Verifies whether the trainee currently has active consent
    def has_active_consent(self):
        return self.consent_status == 'active'


# Tracks granular consent records and audit history for each trainee
class TraineeConsent(models.Model):
    STATUS_CHOICES = (
        ('granted', 'Granted'),
        ('withdrawn', 'Withdrawn'),
    )

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='consents', verbose_name='Trainee')
    consent_version = models.CharField(max_length=20, default='v1.0', verbose_name='Consent Policy Version')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='granted', verbose_name='Status')
    consented_at = models.DateTimeField(default=timezone.now, verbose_name='Consented At')
    withdrawn_at = models.DateTimeField(null=True, blank=True, verbose_name='Withdrawn At')
    source = models.CharField(max_length=100, default='portal_opt_in', verbose_name='Source Channel')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Trainee Consent'
        verbose_name_plural = 'Trainee Consents'
        ordering = ['-created_at']

    # Returns a readable string for the consent record
    def __str__(self):
        return f"Consent for {self.trainee.name}: {self.status} ({self.consent_version})"


# Records verified and self-reported employment placements
class Placement(models.Model):
    EMPLOYMENT_TYPES = (
        ('formal', 'Formal Employment'),
        ('self_employed', 'Self-Employed'),
        ('apprenticeship', 'Apprenticeship'),
        ('informal', 'Informal Sector'),
    )

    SOURCES = (
        ('self_reported', 'Self-Reported'),
        ('employer_confirmed', 'Employer-Confirmed'),
        ('third_party_signal', 'Third-Party Signal'),
    )

    VALIDATION_STATUSES = (
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('disputed', 'Disputed'),
    )

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='placements', verbose_name='Trainee')
    employer_name = models.CharField(max_length=150, verbose_name='Employer / Enterprise Name')
    role = models.CharField(max_length=150, verbose_name='Job Role')
    employment_type = models.CharField(max_length=30, choices=EMPLOYMENT_TYPES, default='formal', verbose_name='Employment Type')
    wage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Monthly Wage (INR)')
    source = models.CharField(max_length=30, choices=SOURCES, default='self_reported', verbose_name='Data Source')
    validation_status = models.CharField(max_length=30, choices=VALIDATION_STATUSES, default='pending', verbose_name='Validation Status')
    start_date = models.DateField(null=True, blank=True, verbose_name='Employment Start Date')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Placement'
        verbose_name_plural = 'Placements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['validation_status']),
            models.Index(fields=['trainee']),
        ]

    # Returns the placement summary string
    def __str__(self):
        return f"{self.trainee.name} at {self.employer_name} ({self.role})"


# Tracks longitudinal follow-ups at 3, 6, and 12-month post-training milestones
class FollowUp(models.Model):
    MILESTONES = (
        ('month_3', '3 Months Post-Training'),
        ('month_6', '6 Months Post-Training'),
        ('month_12', '12 Months Post-Training'),
    )

    CHANNELS = (
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('ivr', 'IVR Call'),
        ('assisted', 'Assisted Outreach'),
    )

    STATUSES = (
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('responded', 'Responded'),
        ('needs_assistance', 'Needs Assistance'),
        ('rescheduled', 'Rescheduled'),
        ('closed', 'Closed'),
    )

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='follow_ups', verbose_name='Trainee')
    milestone = models.CharField(max_length=20, choices=MILESTONES, default='month_3', verbose_name='Milestone')
    channel = models.CharField(max_length=20, choices=CHANNELS, default='whatsapp', verbose_name='Outreach Channel')
    status = models.CharField(max_length=30, choices=STATUSES, default='queued', verbose_name='Status')
    attempts = models.PositiveIntegerField(default=0, verbose_name='Attempts Count')
    due_at = models.DateTimeField(default=timezone.now, verbose_name='Due Date')
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name='Last Attempt At')
    next_contact_date = models.DateField(null=True, blank=True, verbose_name='Next Contact Date')
    response_tag = models.CharField(max_length=100, null=True, blank=True, verbose_name='Response Category')
    trainer_notes = models.TextField(null=True, blank=True, verbose_name='Trainer Outreach Notes')
    notes = models.TextField(null=True, blank=True, verbose_name='Field Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Follow-Up'
        verbose_name_plural = 'Follow-Ups'
        ordering = ['-due_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_at']),
            models.Index(fields=['trainee']),
        ]

    # Returns readable string representation of follow up item
    def __str__(self):
        return f"{self.trainee.name} - {self.milestone} [{self.status}]"

    # Updates the follow-up record when an outreach attempt is made
    def record_attempt(self):
        self.attempts += 1
        self.status = 'sent'
        self.last_attempt_at = timezone.now()
        self.save()

    # Checks whether this follow-up outreach task is overdue
    def is_overdue(self):
        return self.status in ['queued', 'needs_assistance', 'rescheduled'] and self.due_at.date() < timezone.now().date()

    # Checks whether this follow-up is scheduled for action today
    def is_due_today(self):
        return self.due_at.date() == timezone.now().date()


# Records security, data export, and administrative action logs for governance
class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Actor')
    action = models.CharField(max_length=100, verbose_name='Action Performed')
    target_type = models.CharField(max_length=100, verbose_name='Target Type')
    target_id = models.CharField(max_length=100, verbose_name='Target Identifier')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Action Metadata')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']

    # Returns the summary string for the audit log entry
    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.user}: {self.action} on {self.target_type} ({self.target_id})"


# Manages 6-digit email OTPs for registration, login, and password resets
class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ('registration', 'Registration Verification'),
        ('login', 'Login Verification'),
        ('password_reset', 'Password Reset'),
    )

    email = models.EmailField(db_index=True, verbose_name='Email Address')
    otp_code = models.CharField(max_length=6, blank=True, verbose_name='6-Digit OTP (Legacy)')
    otp_hash = models.CharField(max_length=128, blank=True, verbose_name='HMAC Hash of OTP')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Requester IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    expires_at = models.DateTimeField(verbose_name='Expires At')
    attempts = models.PositiveIntegerField(default=0, verbose_name='Failed Attempts')
    is_verified = models.BooleanField(default=False, verbose_name='Is Verified')
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default='registration', verbose_name='Purpose')

    class Meta:
        verbose_name = 'Email OTP'
        verbose_name_plural = 'Email OTPs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'purpose', 'is_verified']),
            models.Index(fields=['created_at']),
        ]

    # Returns readable string representation of the OTP record
    def __str__(self):
        return f"OTP for {self.email} ({self.purpose}) - Verified: {self.is_verified}"

    # Checks if the OTP is currently active, unexpired, and within attempt limits
    def is_valid(self):
        return not self.is_verified and timezone.now() <= self.expires_at and self.attempts < 3

    # Increments failed attempts counter
    def record_failed_attempt(self):
        self.attempts += 1
        self.save()


# Represents a vocational skilling or employment-linked course offered by trainers
class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    )

    trainer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses', verbose_name='Course Trainer')
    title = models.CharField(max_length=200, verbose_name='Course Title')
    course_code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Course Code')
    description = models.TextField(blank=True, verbose_name='Course Description')
    category = models.CharField(max_length=100, default='Vocational Skills', verbose_name='Category')
    provider = models.CharField(max_length=150, blank=True, verbose_name='Training Provider')
    district = models.CharField(max_length=100, blank=True, verbose_name='District Hub')
    state = models.CharField(max_length=100, blank=True, verbose_name='State')
    language = models.CharField(max_length=50, default='English', verbose_name='Instruction Language')
    duration_weeks = models.PositiveIntegerField(default=8, verbose_name='Duration (Weeks)')
    start_date = models.DateField(default=timezone.now, verbose_name='Start Date')
    end_date = models.DateField(null=True, blank=True, verbose_name='End Date')
    capacity = models.PositiveIntegerField(default=30, verbose_name='Student Capacity')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True, verbose_name='Publication Status')
    certificate_eligible = models.BooleanField(default=True, verbose_name='Certificate Eligible')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
            models.Index(fields=['trainer', 'status']),
        ]

    # Returns the course display title and code
    def __str__(self):
        return f"{self.title} ({self.course_code})"

    # Checks if course is open and has available seats for new trainee applications
    def can_accept_applications(self):
        if self.status != 'published':
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return self.available_seats() > 0

    # Returns the count of enrolled trainees
    def active_enrollments_count(self):
        return self.enrollments.filter(status__in=['active', 'completed']).count()

    # Returns remaining available seats before reaching capacity
    def available_seats(self):
        approved_count = self.enrollments.filter(status__in=['active', 'completed']).count()
        return max(0, self.capacity - approved_count)

    # Determines whether course capacity has been reached
    def is_full(self):
        return self.available_seats() <= 0


# Represents an application submitted by a trainee to join a course
class CourseApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications', verbose_name='Course')
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='course_applications', verbose_name='Applicant Trainee')
    motivation = models.TextField(blank=True, verbose_name='Motivation Statement')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name='Application Status')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Submitted At')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Reviewed At')
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications', verbose_name='Reviewer')
    trainer_note = models.TextField(blank=True, null=True, verbose_name='Trainer Decision Note')

    class Meta:
        verbose_name = 'Course Application'
        verbose_name_plural = 'Course Applications'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['course', 'status']),
            models.Index(fields=['trainee', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'trainee'],
                condition=models.Q(status__in=['pending', 'approved']),
                name='unique_active_application_per_trainee_course'
            )
        ]

    # Returns summary string of course application
    def __str__(self):
        return f"{self.trainee.name} -> {self.course.course_code} [{self.status}]"


# Tracks learner enrollment, progression, and completion within a course
class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('withdrawn', 'Withdrawn'),
        ('failed', 'Failed'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Course')
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Enrolled Learner')
    application = models.ForeignKey(CourseApplication, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollments', verbose_name='Originating Application')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True, verbose_name='Enrollment Status')
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='Enrolled At')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Completed At')
    completion_percent = models.PositiveIntegerField(default=0, verbose_name='Completion Percentage')
    completion_notes = models.TextField(blank=True, null=True, verbose_name='Completion Notes')
    marked_completed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_enrollments', verbose_name='Marked Completed By')

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['course', 'status']),
            models.Index(fields=['trainee', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['course', 'trainee'], name='unique_enrollment_per_trainee_course')
        ]

    # Returns readable enrollment description
    def __str__(self):
        return f"{self.trainee.name} in {self.course.course_code} [{self.status}]"

    # Checks if enrollment has achieved completion status
    def is_completed(self):
        return self.status == 'completed'


# Represents an official, verifiable digital credential issued for completed course enrollment
class Certificate(models.Model):
    STATUS_CHOICES = (
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
    )

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate', verbose_name='Course Enrollment')
    certificate_number = models.CharField(max_length=64, unique=True, db_index=True, verbose_name='Certificate Number')
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False, verbose_name='Public Verification Token')
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Issued At')
    issued_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_certificates', verbose_name='Issuing Trainer')
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True, verbose_name='Generated PDF Document')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued', db_index=True, verbose_name='Certificate Status')
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name='Revoked At')
    revocation_reason = models.TextField(blank=True, null=True, verbose_name='Reason for Revocation')

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issued_at']

    # Returns certificate identification string
    def __str__(self):
        return f"Certificate {self.certificate_number} ({self.enrollment.trainee.name})"


# Records post-completion employment and wage outcomes submitted by participants
class TraineeOutcome(models.Model):
    STATUS_CHOICES = (
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed / Own Enterprise'),
        ('unemployed', 'Unemployed'),
        ('seeking_work', 'Actively Seeking Work'),
        ('continuing_education', 'Continuing Higher Education / Training'),
    )

    VERIFICATION_CHOICES = (
        ('self_reported', 'Self Reported'),
        ('verified', 'Verified by Trainer'),
        ('disputed', 'Disputed'),
    )

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='outcome', verbose_name='Linked Course Enrollment')
    employment_status = models.CharField(max_length=35, choices=STATUS_CHOICES, db_index=True, verbose_name='Current Employment Status')
    employer_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Employer or Enterprise Name')
    job_role = models.CharField(max_length=150, blank=True, null=True, verbose_name='Job Role / Designation')
    monthly_earning = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Monthly Earnings (INR)')
    employment_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Employment Contract Type')
    current_district = models.CharField(max_length=100, blank=True, null=True, verbose_name='Current Working District')
    current_state = models.CharField(max_length=100, blank=True, null=True, verbose_name='Current Working State')
    response_notes = models.TextField(blank=True, null=True, verbose_name='Trainee Qualitative Notes')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Submitted At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Last Updated At')
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_outcomes', verbose_name='Verified By')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='self_reported', db_index=True, verbose_name='Verification Status')

    class Meta:
        verbose_name = 'Trainee Outcome'
        verbose_name_plural = 'Trainee Outcomes'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['employment_status', 'verification_status']),
        ]

    # Returns readable outcome string
    def __str__(self):
        return f"Outcome: {self.enrollment.trainee.name} [{self.employment_status}]"


# Manages in-app alerts and notifications delivered to trainers and trainees
class Notification(models.Model):
    TYPE_CHOICES = (
        ('application', 'Course Application'),
        ('enrollment', 'Enrollment Update'),
        ('certificate', 'Certificate Issuance'),
        ('outcome_reminder', 'Outcome Reminder'),
        ('general', 'General Alert'),
    )

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name='Notification Recipient')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications', verbose_name='Sender')
    title = models.CharField(max_length=200, verbose_name='Notification Title')
    body = models.TextField(verbose_name='Message Body')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general', db_index=True, verbose_name='Notification Category')
    is_read = models.BooleanField(default=False, db_index=True, verbose_name='Is Read')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Delivered At')
    related_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications', verbose_name='Related Course')
    related_enrollment = models.ForeignKey(Enrollment, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications', verbose_name='Related Enrollment')

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
        ]

    # Returns notification summary
    def __str__(self):
        return f"Notification to {self.recipient.email}: {self.title}"

