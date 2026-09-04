from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Trainee, TraineeConsent, Placement, FollowUp, AuditLog, EmailOTP

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


# Handles user registration with role restrictions and password validation
class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['trainer', 'trainee'])
    provider = serializers.CharField(max_length=150, required=False, allow_blank=True)
    district = serializers.CharField(max_length=100, required=False, allow_blank=True)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    preferred_language = serializers.CharField(max_length=10, default='en')

    # Validates that the email is not already registered in the system
    def validate_email(self, value):
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


# Serializes placement records linked to trainees
class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = [
            'id', 'trainee', 'employer_name', 'role', 'employment_type',
            'wage', 'source', 'validation_status', 'start_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

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


# Serializes follow-up communication events and actions
class FollowUpSerializer(serializers.ModelSerializer):
    trainee_name = serializers.CharField(source='trainee.name', read_only=True)
    trainee_unified_id = serializers.CharField(source='trainee.unified_id', read_only=True)
    trainee_course = serializers.CharField(source='trainee.course', read_only=True)
    trainee_district = serializers.CharField(source='trainee.district', read_only=True)
    trainee_consent = serializers.CharField(source='trainee.consent_status', read_only=True)

    class Meta:
        model = FollowUp
        fields = [
            'id', 'trainee', 'trainee_name', 'trainee_unified_id',
            'trainee_course', 'trainee_district', 'trainee_consent',
            'milestone', 'channel', 'status', 'attempts', 'due_at',
            'last_attempt_at', 'response_tag', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'attempts', 'last_attempt_at', 'created_at', 'updated_at']


# Serializes complete trainee profiles with related placements and active consent
class TraineeSerializer(serializers.ModelSerializer):
    placements = PlacementSerializer(many=True, read_only=True)
    latest_placement = serializers.SerializerMethodField()
    has_active_consent = serializers.BooleanField(read_only=True)

    class Meta:
        model = Trainee
        fields = [
            'id', 'unified_id', 'name', 'course', 'provider', 'district',
            'state', 'gender', 'age_band', 'stage', 'consent_status',
            'has_active_consent', 'placements', 'latest_placement',
            'created_at', 'updated_at'
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
            'state', 'gender', 'age_band', 'stage', 'consent_status'
        ]

    # Validates that the unified ID is non-empty and formatted cleanly
    def validate_unified_id(self, value):
        clean_id = value.strip().upper()
        if len(clean_id) < 3:
            raise serializers.ValidationError('Unified ID must be at least 3 characters.')
        return clean_id


# Validates password change requests for logged-in users
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    # Validates the new password against standard security constraints
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
