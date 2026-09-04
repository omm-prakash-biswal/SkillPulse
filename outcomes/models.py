from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import random

# Manages user creation and password hashing for CustomUser
class CustomUserManager(BaseUserManager):
    # Creates and saves a standard user with an email and optional Field Atlas ID
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if not extra_fields.get('field_atlas_id'):
            prefix = 'FA-TR' if extra_fields.get('role') == 'trainer' else 'FA-24'
            extra_fields['field_atlas_id'] = f"{prefix}-{random.randint(1000, 9999)}"
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

    # Returns the user display name or falls back to email
    def get_display_name(self):
        return self.full_name or self.email.split('@')[0]

    # Checks if the user has trainer privileges
    def is_trainer_role(self):
        return self.role == 'trainer' or self.is_superuser

    # Checks if the user has trainee privileges
    def is_trainee_role(self):
        return self.role == 'trainee'


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
        ('closed', 'Closed'),
    )

    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name='follow_ups', verbose_name='Trainee')
    milestone = models.CharField(max_length=20, choices=MILESTONES, default='month_3', verbose_name='Milestone')
    channel = models.CharField(max_length=20, choices=CHANNELS, default='whatsapp', verbose_name='Outreach Channel')
    status = models.CharField(max_length=30, choices=STATUSES, default='queued', verbose_name='Status')
    attempts = models.PositiveIntegerField(default=0, verbose_name='Attempts Count')
    due_at = models.DateTimeField(default=timezone.now, verbose_name='Due Date')
    last_attempt_at = models.DateTimeField(null=True, blank=True, verbose_name='Last Attempt At')
    response_tag = models.CharField(max_length=100, null=True, blank=True, verbose_name='Response Category')
    notes = models.TextField(null=True, blank=True, verbose_name='Field Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Follow-Up'
        verbose_name_plural = 'Follow-Ups'
        ordering = ['-due_at']

    # Returns readable string representation of follow up item
    def __str__(self):
        return f"{self.trainee.name} - {self.milestone} [{self.status}]"

    # Updates the follow-up record when an outreach attempt is made
    def record_attempt(self):
        self.attempts += 1
        self.status = 'sent'
        self.last_attempt_at = timezone.now()
        self.save()


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
    otp_code = models.CharField(max_length=6, verbose_name='6-Digit OTP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    expires_at = models.DateTimeField(verbose_name='Expires At')
    attempts = models.PositiveIntegerField(default=0, verbose_name='Failed Attempts')
    is_verified = models.BooleanField(default=False, verbose_name='Is Verified')
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default='registration', verbose_name='Purpose')

    class Meta:
        verbose_name = 'Email OTP'
        verbose_name_plural = 'Email OTPs'
        ordering = ['-created_at']

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
