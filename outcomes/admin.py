from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Trainee, TraineeConsent, Placement, FollowUp, AuditLog, EmailOTP

# Configures the admin interface for CustomUser with role filtering and security fields
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'field_atlas_id', 'role', 'preferred_language', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'preferred_language', 'provider')
    search_fields = ('email', 'full_name', 'field_atlas_id', 'provider', 'phone_number')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'field_atlas_id', 'role', 'phone_number', 'preferred_language', 'profile_photo', 'provider', 'district', 'state', 'address', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


# Configures the admin interface for Trainee with search, filters, and relationship links
@admin.register(Trainee)
class TraineeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unified_id', 'course', 'provider', 'district', 'state', 'stage', 'consent_status', 'updated_at')
    list_filter = ('stage', 'consent_status', 'provider', 'state', 'gender')
    search_fields = ('name', 'unified_id', 'course', 'provider', 'district')
    readonly_fields = ('created_at', 'updated_at')


# Configures the admin interface for TraineeConsent records and audit logs
@admin.register(TraineeConsent)
class TraineeConsentAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'consent_version', 'status', 'consented_at', 'withdrawn_at', 'source')
    list_filter = ('status', 'consent_version', 'source')
    search_fields = ('trainee__name', 'trainee__unified_id')
    readonly_fields = ('created_at',)


# Configures the admin interface for Placements with validation workflows
@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'employer_name', 'role', 'employment_type', 'wage', 'validation_status', 'start_date')
    list_filter = ('employment_type', 'validation_status', 'source')
    search_fields = ('trainee__name', 'employer_name', 'role')
    readonly_fields = ('created_at', 'updated_at')


# Configures the admin interface for FollowUp outreach tracking
@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'milestone', 'channel', 'status', 'attempts', 'due_at', 'last_attempt_at')
    list_filter = ('milestone', 'channel', 'status')
    search_fields = ('trainee__name', 'trainee__unified_id', 'notes')
    readonly_fields = ('created_at', 'updated_at')


# Configures the admin interface for AuditLog viewing
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'target_type', 'target_id')
    list_filter = ('action', 'target_type')
    search_fields = ('action', 'target_type', 'target_id', 'user__email')
    readonly_fields = ('created_at', 'user', 'action', 'target_type', 'target_id', 'metadata')


# Configures the admin interface for EmailOTP auditing
@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'purpose', 'created_at', 'expires_at', 'attempts', 'is_verified')
    list_filter = ('purpose', 'is_verified')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
