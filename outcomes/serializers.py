from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    CustomUser, Trainee, TraineeConsent, Placement, FollowUp, AuditLog, EmailOTP,
    Course, CourseApplication, Enrollment, Certificate, TraineeOutcome, Notification,
    TrainerCourseFeedback
)
from .utils import normalize_provider_name

# Serializes user profile details for authenticated user responses
class CustomUserSerializer(serializers.ModelSerializer):
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'full_name', 'email', 'field_atlas_id', 'role',
            'phone_number', 'preferred_language', 'profile_photo',
            'profile_photo_url', 'provider', 'district', 'state',
            'address', 'bio', 'is_active', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'field_atlas_id', 'role', 'is_active', 'created_at', 'last_login']

    # Returns the absolute or relative URL of the user's profile photo if available
    def get_profile_photo_url(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.profile_photo.url) if request else obj.profile_photo.url
        return None


# Validates and applies editable profile updates for users
class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'phone_number', 'preferred_language',
            'district', 'state', 'address', 'bio', 'provider'
        ]

    # Validates that phone number contains valid characters if provided
    def validate_phone_number(self, value):
        if value and not value.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError('Phone number must contain only digits and standard separators.')
        return value

    # Normalizes provider name to canonical casing if updated
    def validate_provider(self, value):
        return normalize_provider_name(value)


# Handles user registration with Aadhaar validation, mobile, and role restrictions
class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    aadhaar_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    aadhaar_number = serializers.CharField(max_length=30, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    mobile_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['trainer', 'trainee'])
    provider = serializers.CharField(max_length=150, required=False, allow_blank=True)
    district = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    preferred_language = serializers.CharField(max_length=10, default='en')
    otp_code = serializers.CharField(max_length=6, required=False, allow_blank=True)

    # Validates that the email is not already registered in the system if supplied
    def validate_email(self, value):
        if not value:
            return ''
        normalized = value.lower().strip()
        if CustomUser.objects.filter(email=normalized).exists():
            raise serializers.ValidationError('An account with this email address already exists.')
        return normalized

    # Enforces strong password rules on new user registration
    def validate_password(self, value):
        validate_password(value)
        return value

    # Disallows public self-registration as an administrative user
    def validate_role(self, value):
        if value not in ['trainer', 'trainee']:
            raise serializers.ValidationError('Self-registration is restricted to Trainer and Trainee roles.')
        return value

    # Normalizes provider name upon registration
    def validate_provider(self, value):
        return normalize_provider_name(value)


# Serializes placement records linked to trainees
class PlacementSerializer(serializers.ModelSerializer):
    trainee_name = serializers.CharField(source='trainee.name', read_only=True)

    class Meta:
        model = Placement
        fields = [
            'id', 'trainee', 'trainee_name', 'employer_name', 'role', 'employment_type',
            'wage', 'source', 'validation_status', 'start_date',
            'employer_contact_email', 'employer_contact_phone', 'employer_verification_token',
            'employer_verified_at', 'employer_remarks', 'enterprise_name',
            'udyam_registration_number', 'monthly_net_profit', 'workers_employed',
            'apprenticeship_contract_id', 'training_relevance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'employer_verification_token', 'employer_verified_at', 'created_at', 'updated_at']

    # Validates that wage is a non-negative number if entered
    def validate_wage(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Wage cannot be negative.')
        return value


# Serializes consent history entries for trainees
class TraineeConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TraineeConsent
        fields = [
            'id', 'trainee', 'consent_version', 'status',
            'consented_at', 'withdrawn_at', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Serializes follow-up communication events with overdue and due-today indicators
class FollowUpSerializer(serializers.ModelSerializer):
    trainee_name = serializers.CharField(source='trainee.name', read_only=True)
    trainee_unified_id = serializers.CharField(source='trainee.unified_id', read_only=True)
    trainee_course = serializers.CharField(source='trainee.course', read_only=True)
    trainee_district = serializers.CharField(source='trainee.district', read_only=True)
    trainee_consent = serializers.CharField(source='trainee.consent_status', read_only=True)
    trainee_alternate_phone = serializers.CharField(source='trainee.alternate_phone_number', read_only=True)
    trainee_secondary_contact = serializers.CharField(source='trainee.secondary_contact_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_due_today = serializers.BooleanField(read_only=True)

    class Meta:
        model = FollowUp
        fields = [
            'id', 'trainee', 'trainee_name', 'trainee_unified_id',
            'trainee_course', 'trainee_district', 'trainee_consent',
            'trainee_alternate_phone', 'trainee_secondary_contact',
            'milestone', 'channel', 'status', 'attempts', 'due_at',
            'last_attempt_at', 'next_contact_date', 'response_tag',
            'reported_wage', 'attrition_reason', 'escalated_to_mobilizer',
            'escalation_notes', 'trainer_notes', 'notes', 'is_overdue', 'is_due_today',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'attempts', 'last_attempt_at', 'is_overdue', 'is_due_today', 'created_at', 'updated_at']


# Serializes complete trainee profiles with related placements and active consent
class TraineeSerializer(serializers.ModelSerializer):
    placements = PlacementSerializer(many=True, read_only=True)
    latest_placement = serializers.SerializerMethodField()
    has_active_consent = serializers.BooleanField(read_only=True)
    assigned_trainer_name = serializers.CharField(source='assigned_trainer.full_name', read_only=True)

    class Meta:
        model = Trainee
        fields = [
            'id', 'unified_id', 'name', 'course', 'provider', 'district',
            'state', 'gender', 'age_band', 'stage', 'consent_status',
            'baseline_wage', 'alternate_phone_number', 'secondary_contact_name', 'secondary_contact_relation',
            'has_active_consent', 'assigned_trainer', 'assigned_trainer_name',
            'placements', 'latest_placement', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Returns the most recent placement record for the trainee if one exists
    def get_latest_placement(self, obj):
        latest = obj.placements.order_by('-created_at').first()
        if latest:
            return PlacementSerializer(latest).data
        return None


# Validates input payload when creating or modifying trainee records
class TraineeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainee
        fields = [
            'unified_id', 'name', 'course', 'provider', 'district',
            'state', 'gender', 'age_band', 'stage', 'consent_status',
            'baseline_wage', 'alternate_phone_number', 'secondary_contact_name', 'secondary_contact_relation'
        ]

    # Validates that the unified ID is non-empty and formatted cleanly
    def validate_unified_id(self, value):
        clean_id = value.strip().upper()
        if len(clean_id) < 3:
            raise serializers.ValidationError('Unified ID must be at least 3 characters.')
        return clean_id

    # Normalizes provider name to canonical standard upon trainee registration
    def validate_provider(self, value):
        return normalize_provider_name(value)


# Validates password change requests for logged-in users with strong password rules
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    # Validates the new password against standard security constraints
    def validate_new_password(self, value):
        validate_password(value)
        return value


# Validates password reset submissions with email OTP and password strength rules
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True)

    # Enforces standard Django password complexity rules on reset password
    def validate_new_password(self, value):
        validate_password(value)
        return value


# Serializes audit log events for compliance inspection
class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'actor_email', 'action', 'target_type', 'target_id', 'metadata', 'created_at']
        read_only_fields = fields


# Serializes course details with live capacity and student status metrics
class CourseSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)
    enrolled_count = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    can_apply = serializers.SerializerMethodField()
    user_application_status = serializers.SerializerMethodField()
    user_enrollment_id = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'trainer', 'trainer_name', 'title', 'course_code', 'description',
            'category', 'provider', 'district', 'state', 'language', 'duration_weeks',
            'start_date', 'end_date', 'capacity', 'status', 'certificate_eligible',
            'enrolled_count', 'available_seats', 'is_full', 'can_apply',
            'user_application_status', 'user_enrollment_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'trainer', 'created_at', 'updated_at']

    # Returns the count of learners actively enrolled or graduated in the course
    def get_enrolled_count(self, obj):
        return obj.active_enrollments_count()

    # Returns remaining capacity seats for upcoming applicants
    def get_available_seats(self, obj):
        return obj.available_seats()

    # Indicates whether course enrollment capacity has been exhausted
    def get_is_full(self, obj):
        return obj.is_full()

    # Checks if course is open for new applicant submissions
    def get_can_apply(self, obj):
        return obj.can_accept_applications()

    # Returns current applicant status for the logged-in trainee
    def get_user_application_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        trainee = getattr(request.user, 'trainee_profile', None)
        if not trainee:
            return None
        app = obj.applications.filter(trainee=trainee).order_by('-submitted_at').first()
        return app.status if app else None

    # Returns active enrollment ID for the logged-in trainee if enrolled
    def get_user_enrollment_id(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        trainee = getattr(request.user, 'trainee_profile', None)
        if not trainee:
            return None
        enrollment = obj.enrollments.filter(trainee=trainee).first()
        return enrollment.id if enrollment else None


# Validates payload for creating or modifying course offerings
class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'title', 'course_code', 'description', 'category', 'provider',
            'district', 'state', 'language', 'duration_weeks', 'start_date',
            'end_date', 'capacity', 'status', 'certificate_eligible'
        ]

    # Validates and standardizes uppercase format for course codes
    def validate_course_code(self, value):
        cleaned = value.strip().upper()
        if len(cleaned) < 3:
            raise serializers.ValidationError('Course code must be at least 3 characters.')
        return cleaned

    # Validates date logic and positive seating limits
    def validate(self, data):
        if 'start_date' not in data and not getattr(self.instance, 'start_date', None):
            data['start_date'] = timezone.now().date()
        if 'end_date' not in data and not getattr(self.instance, 'end_date', None):
            weeks = data.get('duration_weeks', getattr(self.instance, 'duration_weeks', 8)) or 8
            data['end_date'] = data['start_date'] + timedelta(weeks=weeks)

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({'end_date': 'End date must be on or after start date.'})
        capacity = data.get('capacity', getattr(self.instance, 'capacity', 30))
        if capacity is not None and capacity <= 0:
            raise serializers.ValidationError({'capacity': 'Capacity must be at least 1 student.'})
        return data


# Serializes course application requests with learner details
class CourseApplicationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    trainee_name = serializers.CharField(source='trainee.name', read_only=True)
    trainee_unified_id = serializers.CharField(source='trainee.unified_id', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.full_name', read_only=True)

    class Meta:
        model = CourseApplication
        fields = [
            'id', 'course', 'course_title', 'course_code', 'trainee',
            'trainee_name', 'trainee_unified_id', 'motivation', 'status',
            'submitted_at', 'reviewed_at', 'reviewed_by_name', 'trainer_note'
        ]
        read_only_fields = ['id', 'trainee', 'status', 'submitted_at', 'reviewed_at', 'reviewed_by_name', 'trainer_note']


# Validates trainer decision notes when approving or rejecting learner applications
class CourseApplicationReviewSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    action = serializers.CharField(required=False)
    trainer_note = serializers.CharField(required=False, allow_blank=True)
    review_notes = serializers.CharField(required=False, allow_blank=True)

    # Validates decision status and standardizes review payload
    def validate(self, data):
        decision = data.get('status') or data.get('action')
        if not decision:
            raise serializers.ValidationError({'status': 'Decision status or action is required.'})
        decision = decision.strip().lower()
        if decision in ['approve', 'approved']:
            data['status'] = 'approved'
        elif decision in ['reject', 'rejected']:
            data['status'] = 'rejected'
        else:
            raise serializers.ValidationError({'status': 'Status must be approved or rejected.'})

        note = data.get('trainer_note') or data.get('review_notes') or ''
        data['trainer_note'] = note
        return data


# Serializes student enrollment records with certificate and outcome linkages
class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_category = serializers.CharField(source='course.category', read_only=True)
    trainee_name = serializers.CharField(source='trainee.name', read_only=True)
    trainee_unified_id = serializers.CharField(source='trainee.unified_id', read_only=True)
    trainee_district = serializers.CharField(source='trainee.district', read_only=True)
    marked_completed_by_name = serializers.CharField(source='marked_completed_by.full_name', read_only=True)
    has_certificate = serializers.SerializerMethodField()
    certificate_id = serializers.SerializerMethodField()
    certificate_token = serializers.SerializerMethodField()
    certificate_pdf_url = serializers.SerializerMethodField()
    has_outcome = serializers.SerializerMethodField()
    outcome_status = serializers.SerializerMethodField()
    outcome_id = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_title', 'course_code', 'course_category',
            'trainee', 'trainee_name', 'trainee_unified_id', 'trainee_district',
            'application', 'status', 'enrolled_at', 'completed_at',
            'completion_percent', 'completion_notes', 'marked_completed_by_name',
            'has_certificate', 'certificate_id', 'certificate_token', 'certificate_pdf_url',
            'has_outcome', 'outcome_status', 'outcome_id'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at', 'marked_completed_by_name']

    # Indicates whether a valid completion certificate has been issued
    def get_has_certificate(self, obj):
        return hasattr(obj, 'certificate') and obj.certificate.status == 'issued'

    # Returns the primary key of the issued certificate
    def get_certificate_id(self, obj):
        return obj.certificate.id if hasattr(obj, 'certificate') and obj.certificate.status == 'issued' else None

    # Returns the UUID verification token of the issued certificate
    def get_certificate_token(self, obj):
        return str(obj.certificate.verification_token) if hasattr(obj, 'certificate') and obj.certificate.status == 'issued' else None

    # Returns the media download URL for the certificate PDF
    def get_certificate_pdf_url(self, obj):
        if hasattr(obj, 'certificate') and obj.certificate.status == 'issued' and obj.certificate.pdf_file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.certificate.pdf_file.url) if request else obj.certificate.pdf_file.url
        return None

    # Indicates whether an employment outcome has been reported
    def get_has_outcome(self, obj):
        return hasattr(obj, 'outcome')

    # Returns the employment status reported in the linked outcome
    def get_outcome_status(self, obj):
        return obj.outcome.employment_status if hasattr(obj, 'outcome') else None

    # Returns the primary key of the linked outcome record
    def get_outcome_id(self, obj):
        return obj.outcome.id if hasattr(obj, 'outcome') else None


# Validates trainer updates to student progression or course graduation
class EnrollmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['status', 'completion_percent', 'completion_notes']

    # Validates completion percentage is bounded within 0 and 100
    def validate_completion_percent(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Completion percentage must be between 0 and 100.')
        return value


# Serializes verifiable certificates with digital signatures and verification links
class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='enrollment.course.title', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.course_code', read_only=True)
    course_category = serializers.CharField(source='enrollment.course.category', read_only=True)
    trainee_name = serializers.CharField(source='enrollment.trainee.name', read_only=True)
    trainee_unified_id = serializers.CharField(source='enrollment.trainee.unified_id', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.full_name', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    verification_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = [
            'id', 'enrollment', 'course_title', 'course_code', 'course_category',
            'trainee_name', 'trainee_unified_id', 'certificate_number',
            'verification_token', 'issued_at', 'issued_by_name', 'pdf_url',
            'verification_url', 'status', 'revoked_at', 'revocation_reason'
        ]
        read_only_fields = ['id', 'certificate_number', 'verification_token', 'issued_at', 'issued_by_name', 'pdf_url']

    # Resolves media URL for generated certificate PDF document
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.pdf_file.url) if request else obj.pdf_file.url
        return None

    # Builds public verification endpoint path
    def get_verification_url(self, obj):
        return f"/certificate/verify/{obj.verification_token}/"


# Serializes post-course employment, wage, and livelihood outcome surveys
class TraineeOutcomeSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='enrollment.course.title', read_only=True)
    course_code = serializers.CharField(source='enrollment.course.course_code', read_only=True)
    trainee_name = serializers.CharField(source='enrollment.trainee.name', read_only=True)
    trainee_unified_id = serializers.CharField(source='enrollment.trainee.unified_id', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.full_name', read_only=True)

    class Meta:
        model = TraineeOutcome
        fields = [
            'id', 'enrollment', 'course_title', 'course_code', 'trainee_name',
            'trainee_unified_id', 'employment_status', 'employer_name', 'job_role',
            'monthly_earning', 'employment_type', 'current_district', 'current_state',
            'training_relevance', 'non_placement_reason', 'skill_gap', 'attrition_reason',
            'enterprise_name', 'udyam_registration_number', 'monthly_net_profit',
            'workers_employed', 'apprenticeship_contract_id',
            'response_notes', 'submitted_at', 'updated_at', 'verification_status',
            'verified_by_name'
        ]
        read_only_fields = ['id', 'submitted_at', 'updated_at', 'verification_status', 'verified_by_name']


# Validates trainee input when reporting or updating employment outcomes
class TraineeOutcomeSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TraineeOutcome
        fields = [
            'employment_status', 'employer_name', 'job_role', 'monthly_earning',
            'employment_type', 'current_district', 'current_state',
            'training_relevance', 'non_placement_reason', 'skill_gap', 'attrition_reason',
            'enterprise_name', 'udyam_registration_number', 'monthly_net_profit',
            'workers_employed', 'apprenticeship_contract_id',
            'response_notes'
        ]

    # Validates non-negative monthly earnings
    def validate_monthly_earning(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Monthly earning cannot be negative.')
        return value


# Validates public tokenized employer verification action
class EmployerPlacementVerificationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['confirm', 'dispute'])
    remarks = serializers.CharField(required=False, allow_blank=True, default='')
    employer_remarks = serializers.CharField(required=False, allow_blank=True, default='')
    verified_wage = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)


# Serializes in-app user notifications and delivery status
class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    related_course_title = serializers.CharField(source='related_course.title', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_name', 'title', 'body',
            'type', 'is_read', 'created_at', 'related_course',
            'related_course_title', 'related_enrollment'
        ]
        read_only_fields = ['id', 'recipient', 'sender', 'sender_name', 'created_at', 'related_course_title']


# Serializes feedback and ratings submitted by trainees for trainers and courses
class TrainerCourseFeedbackSerializer(serializers.ModelSerializer):
    trainee_name = serializers.CharField(source='trainee.name', read_only=True)
    trainer_name = serializers.CharField(source='trainer.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)

    class Meta:
        model = TrainerCourseFeedback
        fields = [
            'id', 'trainee', 'trainee_name', 'trainer', 'trainer_name',
            'course', 'course_title', 'course_code',
            'trainer_behavior_rating', 'trainer_teaching_rating', 'trainer_doubt_clearing_rating',
            'course_practical_rating', 'course_content_rating', 'overall_score',
            'feedback_tags', 'opinion_text', 'would_recommend', 'status',
            'created_at'
        ]
        read_only_fields = ['id', 'trainee_name', 'trainer_name', 'course_title', 'course_code', 'overall_score', 'created_at']

    def create(self, validated_data):
        # Calculate overall score as weighted average
        b = validated_data.get('trainer_behavior_rating', 5)
        t = validated_data.get('trainer_teaching_rating', 5)
        d = validated_data.get('trainer_doubt_clearing_rating', 5)
        p = validated_data.get('course_practical_rating', 5)
        c = validated_data.get('course_content_rating', 5)
        avg = round((b + t + d + p + c) / 5.0, 2)
        validated_data['overall_score'] = avg
        return super().create(validated_data)


