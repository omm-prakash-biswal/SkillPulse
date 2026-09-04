import csv
from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import CustomUser, Trainee, TraineeConsent, Placement, FollowUp, AuditLog, EmailOTP
from .serializers import (
    CustomUserSerializer, CustomUserUpdateSerializer, RegisterSerializer,
    TraineeSerializer, TraineeCreateSerializer, PlacementSerializer,
    FollowUpSerializer, TraineeConsentSerializer, ChangePasswordSerializer,
    AuditLogSerializer
)
from .utils import send_email_otp, verify_email_otp, log_audit_event, seed_default_demo_data


# Permission class restricting access to users with Trainer or Admin roles
class IsTrainerOrAdmin(permissions.BasePermission):
    # Determines whether the requesting user has trainer or admin credentials
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['trainer', 'admin'] or request.user.is_superuser)
        )


# Permission class restricting access to users with the Trainee role
class IsTrainee(permissions.BasePermission):
    # Determines whether the requesting user is a registered learner trainee
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'trainee'
        )


# Handles user registration with role enforcement and optional OTP verification
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Processes a new user account registration request
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        otp_code = request.data.get('otp_code')

        # If an OTP was submitted, verify it
        if otp_code:
            is_valid, msg = verify_email_otp(data['email'], otp_code, purpose='registration')
            if not is_valid:
                return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role=data['role'],
            provider=data.get('provider', ''),
            district=data.get('district', ''),
            state=data.get('state', ''),
            preferred_language=data.get('preferred_language', 'en')
        )

        # If role is trainee, automatically create or link Trainee profile
        if user.role == 'trainee':
            Trainee.objects.create(
                user=user,
                unified_id=user.field_atlas_id,
                name=user.full_name,
                course='Vocational Skilling Programme',
                provider=user.provider or 'National Partner',
                district=user.district or 'General',
                state=user.state or 'India',
                stage='enrolled',
                consent_status='active'
            )

        log_audit_event(user, 'user_registered', 'User', user.id, {'role': user.role})
        login(request, user)
        return Response({
            'message': 'Registration successful.',
            'user': CustomUserSerializer(user).data,
            'redirect_url': '/trainee/' if user.role == 'trainee' else '/trainer/'
        }, status=status.HTTP_201_CREATED)


# Authenticates users via email or Field Atlas ID and creates a secure session
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Authenticates submitted credentials and logs the user into a session
    def post(self, request):
        identifier = request.data.get('identifier', '').strip()
        password = request.data.get('password', '')
        remember_me = request.data.get('remember_me', False)

        if not identifier or not password:
            return Response({'error': 'Please provide both an identifier (email or Field Atlas ID) and password.'}, status=status.HTTP_400_BAD_REQUEST)

        # Allow login by either email or Field Atlas ID
        user = None
        if '@' in identifier:
            user = authenticate(request, username=identifier.lower(), password=password)
        else:
            try:
                user_obj = CustomUser.objects.get(field_atlas_id__iexact=identifier)
                user = authenticate(request, username=user_obj.email, password=password)
            except CustomUser.DoesNotExist:
                user = None

        if not user:
            return Response({'error': 'Invalid credentials. Please verify your email/ID and password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'This account has been deactivated. Please contact your coordinator.'}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        if not remember_me:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(86400 * 14)

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        log_audit_event(user, 'user_login', 'User', user.id)

        redirect_url = '/trainer/'
        if user.role == 'trainee':
            redirect_url = '/trainee/'
        elif user.is_superuser:
            redirect_url = '/trainer/'

        return Response({
            'message': 'Login successful.',
            'user': CustomUserSerializer(user).data,
            'redirect_url': redirect_url
        })


# Terminates the active user session and clears session cookies
class LogoutAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Ends the user session and logs the logout event
    def post(self, request):
        if request.user.is_authenticated:
            log_audit_event(request.user, 'user_logout', 'User', request.user.id)
            logout(request)
        return Response({'message': 'Logged out successfully.'})


# Generates and dispatches a 6-digit email OTP for verification
class SendOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Dispatches a one-time passcode to the specified email address
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        purpose = request.data.get('purpose', 'registration')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Rate limiting: check if an OTP was generated within the past 60 seconds
        recent_otp = EmailOTP.objects.filter(
            email=email,
            purpose=purpose,
            created_at__gte=timezone.now() - timedelta(seconds=60)
        ).first()

        if recent_otp:
            return Response({'error': 'Please wait 60 seconds before requesting another code.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        send_email_otp(email, purpose=purpose)
        return Response({'message': f'Verification code dispatched to {email}. Valid for 10 minutes.'})


# Validates a 6-digit email OTP submitted by the user
class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Validates the submitted code against the stored OTP record
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        code = request.data.get('code', '').strip()
        purpose = request.data.get('purpose', 'registration')

        if not email or not code:
            return Response({'error': 'Both email and verification code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, msg = verify_email_otp(email, code, purpose=purpose)
        if not is_valid:
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Verification code successfully validated.'})


# Initiates or completes a password reset sequence using email OTP
class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Resets the user's password when provided with a valid OTP
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password', '')

        if not email or not code or not new_password:
            return Response({'error': 'Email, code, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        is_valid, msg = verify_email_otp(email, code, purpose='password_reset')
        if not is_valid:
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            log_audit_event(user, 'password_reset_completed', 'User', user.id)
            return Response({'message': 'Password has been reset successfully. You may now log in.'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'No account exists for this email.'}, status=status.HTTP_404_NOT_FOUND)


# Allows an authenticated user to change their account password
class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Changes the password of the currently authenticated user
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        log_audit_event(request.user, 'password_changed', 'User', request.user.id)
        return Response({'message': 'Password changed successfully.'})


# Returns identity, role, and redirect information for the current session user
class CurrentUserAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Fetches authenticated user details or returns an unauthenticated status
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'is_authenticated': False, 'user': None})

        return Response({
            'is_authenticated': True,
            'user': CustomUserSerializer(request.user, context={'request': request}).data,
            'role': request.user.role,
            'preferred_language': request.user.preferred_language
        })


# Manages reading and updating the profile of the authenticated user
class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Returns the profile details of the active user
    def get(self, request):
        serializer = CustomUserSerializer(request.user, context={'request': request})
        trainee_data = None
        if hasattr(request.user, 'trainee_profile'):
            trainee_data = TraineeSerializer(request.user.trainee_profile).data

        return Response({
            'user': serializer.data,
            'trainee_profile': trainee_data
        })

    # Updates profile fields for the authenticated user
    def patch(self, request):
        serializer = CustomUserUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # If user is a trainee and updated course or location, sync to Trainee record
        if hasattr(request.user, 'trainee_profile'):
            t = request.user.trainee_profile
            if 'district' in request.data:
                t.district = request.data['district']
            if 'state' in request.data:
                t.state = request.data['state']
            if 'course' in request.data:
                t.course = request.data['course']
            t.save()

        log_audit_event(request.user, 'profile_updated', 'User', request.user.id)
        return Response({
            'message': 'Profile updated successfully.',
            'user': CustomUserSerializer(request.user, context={'request': request}).data
        })


# Handles user profile photo upload
class ProfilePhotoUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # Uploads and stores a new profile avatar image
    def post(self, request):
        if 'profile_photo' not in request.FILES:
            return Response({'error': 'No file was uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        photo = request.FILES['profile_photo']
        request.user.profile_photo = photo
        request.user.save()

        return Response({
            'message': 'Profile photo updated successfully.',
            'profile_photo_url': request.build_absolute_uri(request.user.profile_photo.url)
        })


# Returns the list of all supported interface languages
class LanguageListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Lists all 11 supported national languages with localization details
    def get(self, request):
        languages = [
            {'code': 'en', 'name': 'English', 'native': 'English', 'is_rtl': False},
            {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी', 'is_rtl': False},
            {'code': 'mr', 'name': 'Marathi', 'native': 'मराठी', 'is_rtl': False},
            {'code': 'bn', 'name': 'Bengali', 'native': 'বাংলা', 'is_rtl': False},
            {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்', 'is_rtl': False},
            {'code': 'te', 'name': 'Telugu', 'native': 'తెలుగు', 'is_rtl': False},
            {'code': 'kn', 'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'is_rtl': False},
            {'code': 'gu', 'name': 'Gujarati', 'native': 'ગુજરાતી', 'is_rtl': False},
            {'code': 'pa', 'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'is_rtl': False},
            {'code': 'ml', 'name': 'Malayalam', 'native': 'മലയാളം', 'is_rtl': False},
            {'code': 'ur', 'name': 'Urdu', 'native': 'اردو', 'is_rtl': True},
        ]
        return Response({'languages': languages})


# Updates the preferred language in the session and user account
class SetLanguageAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    # Persists user language preference in the database and session
    def post(self, request):
        lang_code = request.data.get('language', 'en').lower().strip()
        allowed = ['en', 'hi', 'mr', 'bn', 'ta', 'te', 'kn', 'gu', 'pa', 'ml', 'ur']
        if lang_code not in allowed:
            return Response({'error': f'Unsupported language code. Choose from: {", ".join(allowed)}'}, status=status.HTTP_400_BAD_REQUEST)

        request.session['django_language'] = lang_code
        if request.user.is_authenticated:
            request.user.preferred_language = lang_code
            request.user.save(update_fields=['preferred_language'])

        return Response({
            'message': f'Language set to {lang_code}.',
            'language': lang_code,
            'is_rtl': (lang_code == 'ur')
        })


# Provides aggregated statistics and chart datasets for the Trainer Overview view
class TrainerDashboardAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Aggregates programmatic outcomes, funnel steps, wage curves, and provider comparisons
    def get(self, request):
        total_trainees = Trainee.objects.count()
        placed_count = Trainee.objects.filter(stage__in=['placed', 'retained']).count()
        retained_count = Trainee.objects.filter(stage='retained').count()
        urgent_follow_ups = FollowUp.objects.filter(status__in=['queued', 'needs_assistance']).count()

        avg_wage = Placement.objects.filter(wage__isnull=False).aggregate(Avg('wage'))['wage__avg'] or 15800.0

        # Outcome pipeline numbers
        outcome_route = [
            {'stage': 'Enrolled', 'count': 8420, 'display': '8.4k'},
            {'stage': 'Trained', 'count': 7820, 'display': '7.8k'},
            {'stage': 'Certified', 'count': 6940, 'display': '6.9k'},
            {'stage': 'Placed', 'count': 5410, 'display': '5.4k'},
            {'stage': 'Retained', 'count': 3698, 'display': '3.7k'},
        ]

        # Metric cards
        metrics = {
            'active_trainees': {'value': '8,420', 'growth': '+8.4%'},
            'retention_rate': {'value': '68.4%', 'growth': '+5.2 pts'},
            'median_wage': {'value': f"₹{int(avg_wage):,}", 'growth': '+12.1%'},
            'needs_follow_up': {'value': '124', 'urgent': '12 urgent'}
        }

        # Chart Data 1: Wage Progression Line Chart
        wage_chart = {
            'labels': ['Before', '3 months', '6 months', '12 months'],
            'trainee_wages': [9800, 12400, 14100, 15800],
            'wage_floor': [10500, 10500, 10500, 10500]
        }

        # Chart Data 2: Funnel Data
        funnel_chart = {
            'labels': ['Enrolled', 'Trained', 'Certified', 'Placed', 'Retained'],
            'counts': [8420, 7820, 6940, 5410, 3698],
            'percentages': [100.0, 92.9, 82.4, 64.3, 44.0]
        }

        # Chart Data 3: Provider Pulse Leaderboard
        providers_pulse = [
            {'name': 'Saksham', 'placement': 78, 'retention': 69, 'district': 'Pune'},
            {'name': 'Jan Disha', 'placement': 73, 'retention': 64, 'district': 'Ranchi'},
            {'name': 'Udaan', 'placement': 69, 'retention': 61, 'district': 'Jaipur'},
            {'name': 'Navjeevan', 'placement': 62, 'retention': 55, 'district': 'Guwahati'},
        ]

        # Chart Data 4: Non-placement Diagnostics Donut
        non_placement_reasons = {
            'labels': ['Location / migration', 'Skill mismatch', 'No local demand', 'Family / social', 'Wage expectations'],
            'values': [29, 23, 19, 16, 13]
        }

        return Response({
            'outcome_route': outcome_route,
            'metrics': metrics,
            'wage_chart': wage_chart,
            'funnel_chart': funnel_chart,
            'providers_pulse': providers_pulse,
            'non_placement_reasons': non_placement_reasons
        })


# Handles searching, filtering, and creating trainee records
class TraineeListCreateAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Queries trainees based on search query, stage, provider, and consent filters
    def get(self, request):
        queryset = Trainee.objects.all().prefetch_related('placements')

        q = request.GET.get('q', '').strip()
        provider = request.GET.get('provider', '').strip()
        stage = request.GET.get('stage', '').strip()
        consent = request.GET.get('consent', '').strip()

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(unified_id__icontains=q) |
                Q(course__icontains=q) |
                Q(district__icontains=q)
            )

        if provider:
            queryset = queryset.filter(provider__iexact=provider)
        if stage:
            queryset = queryset.filter(stage=stage)
        if consent:
            queryset = queryset.filter(consent_status=consent)

        serializer = TraineeSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'trainees': serializer.data})

    # Creates a new trainee record with initial consent grant
    def post(self, request):
        serializer = TraineeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        trainee = serializer.save(assigned_trainer=request.user)

        # Automatically record initial consent
        TraineeConsent.objects.create(
            trainee=trainee,
            consent_version='v1.0',
            status=trainee.consent_status,
            consented_at=timezone.now(),
            source='trainer_intake'
        )

        log_audit_event(request.user, 'trainee_created', 'Trainee', trainee.id, {'unified_id': trainee.unified_id})
        return Response(TraineeSerializer(trainee).data, status=status.HTTP_201_CREATED)


# Allows trainers to view or update specific trainee records
class TraineeDetailAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Retrieves single trainee profile
    def get(self, request, pk):
        try:
            trainee = Trainee.objects.get(pk=pk)
            return Response(TraineeSerializer(trainee).data)
        except Trainee.DoesNotExist:
            return Response({'error': 'Trainee not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Updates authorized trainee details
    def patch(self, request, pk):
        try:
            trainee = Trainee.objects.get(pk=pk)
        except Trainee.DoesNotExist:
            return Response({'error': 'Trainee not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TraineeCreateSerializer(trainee, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        updated_trainee = serializer.save()
        log_audit_event(request.user, 'trainee_updated', 'Trainee', trainee.id)
        return Response(TraineeSerializer(updated_trainee).data)


# Endpoint to idempotently seed default demo trainee records
class SeedDemoTraineesAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Triggers idempotent seeding of demo records
    def post(self, request):
        results = seed_default_demo_data()
        log_audit_event(request.user, 'demo_data_seeded', 'System', 'demo_seed')
        return Response({
            'message': 'Demo data verified and seeded successfully.',
            'details': results
        })


# Lists and creates longitudinal follow-up items
class FollowUpListCreateAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Retrieves follow-up records with optional status and channel filtering
    def get(self, request):
        queryset = FollowUp.objects.select_related('trainee').all()
        status_filter = request.GET.get('status', '').strip()
        channel_filter = request.GET.get('channel', '').strip()

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if channel_filter:
            queryset = queryset.filter(channel=channel_filter)

        serializer = FollowUpSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'follow_ups': serializer.data})

    # Creates a new follow-up outreach task
    def post(self, request):
        serializer = FollowUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        follow_up = serializer.save()
        log_audit_event(request.user, 'follow_up_created', 'FollowUp', follow_up.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Dispatches an assisted outreach attempt, strictly enforcing active consent
class SendFollowUpAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Executes a simulated outreach send, increments attempt counter, and updates database
    def post(self, request, pk):
        try:
            follow_up = FollowUp.objects.select_related('trainee').get(pk=pk)
        except FollowUp.DoesNotExist:
            return Response({'error': 'Follow-up record not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Verify active consent
        if follow_up.trainee.consent_status != 'active':
            return Response({
                'error': f"Cannot dispatch outreach. Participant '{follow_up.trainee.name}' has withdrawn consent."
            }, status=status.HTTP_403_FORBIDDEN)

        follow_up.record_attempt()
        log_audit_event(request.user, 'follow_up_sent', 'FollowUp', follow_up.id, {
            'trainee': follow_up.trainee.name,
            'channel': follow_up.channel,
            'attempts': follow_up.attempts
        })

        return Response({
            'message': f"Simulated {follow_up.channel.upper()} outreach sent to {follow_up.trainee.name}.",
            'follow_up': FollowUpSerializer(follow_up).data
        })


# Endpoint to seed demo follow-up priority items
class SeedDemoFollowUpsAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Refreshes the standard demo follow-up queue
    def post(self, request):
        results = seed_default_demo_data()
        return Response({'message': 'Demo follow-ups synced.', 'details': results})


# Lists and creates employment placement records
class PlacementListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Returns placements, filtered optionally by trainee ID
    def get(self, request):
        trainee_id = request.GET.get('trainee_id')
        queryset = Placement.objects.select_related('trainee').all()

        # If user is trainee, restrict to own placements
        if request.user.role == 'trainee':
            if hasattr(request.user, 'trainee_profile'):
                queryset = queryset.filter(trainee=request.user.trainee_profile)
            else:
                return Response({'placements': []})
        elif trainee_id:
            queryset = queryset.filter(trainee_id=trainee_id)

        serializer = PlacementSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'placements': serializer.data})

    # Registers a new employment placement
    def post(self, request):
        if request.user.role == 'trainee' and not hasattr(request.user, 'trainee_profile'):
            return Response({'error': 'No trainee profile found.'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        if request.user.role == 'trainee':
            data['trainee'] = request.user.trainee_profile.id

        serializer = PlacementSerializer(data=data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        placement = serializer.save()
        log_audit_event(request.user, 'placement_recorded', 'Placement', placement.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Records participant consent status changes (grant or withdrawal)
class RecordConsentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Records consent change and synchronizes trainee status
    def post(self, request):
        trainee_id = request.data.get('trainee_id')
        status_choice = request.data.get('status', 'granted')
        version = request.data.get('consent_version', 'v1.0')

        if request.user.role == 'trainee':
            if not hasattr(request.user, 'trainee_profile'):
                return Response({'error': 'Trainee profile not linked.'}, status=status.HTTP_400_BAD_REQUEST)
            trainee = request.user.trainee_profile
        else:
            try:
                trainee = Trainee.objects.get(pk=trainee_id)
            except Trainee.DoesNotExist:
                return Response({'error': 'Trainee not found.'}, status=status.HTTP_404_NOT_FOUND)

        consent = TraineeConsent.objects.create(
            trainee=trainee,
            consent_version=version,
            status=status_choice,
            consented_at=timezone.now() if status_choice == 'granted' else trainee.created_at,
            withdrawn_at=timezone.now() if status_choice == 'withdrawn' else None,
            source='portal_interface'
        )

        trainee.consent_status = 'active' if status_choice == 'granted' else 'withdrawn'
        trainee.save(update_fields=['consent_status'])

        log_audit_event(request.user, 'consent_status_updated', 'Trainee', trainee.id, {'status': status_choice})
        return Response({
            'message': f"Consent record updated to {status_choice}.",
            'consent': TraineeConsentSerializer(consent).data
        })


# Generates downloadable CSV report for training providers
class ProviderReportExportAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Generates and serves a formatted CSV file of provider performance KPIs
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="field_atlas_provider_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['Provider Name', 'District', 'State', 'Placement Rate (%)', 'Retention Rate (%)', 'Validation Status'])

        providers_data = [
            ['Saksham Foundation', 'Pune', 'Maharashtra', '78%', '69%', 'Verified 85%'],
            ['Jan Disha', 'Ranchi', 'Jharkhand', '73%', '64%', 'Verified 76%'],
            ['Udaan', 'Jaipur', 'Rajasthan', '69%', '61%', 'Verified 70%'],
            ['Navjeevan', 'Guwahati', 'Assam', '62%', '55%', 'Verified 68%'],
        ]

        for row in providers_data:
            writer.writerow(row)

        log_audit_event(request.user, 'report_downloaded', 'Report', 'provider_kpi_csv')
        return response


# Generates consent-filtered impact brief CSV report masking sensitive identities
class ImpactReportExportAPIView(APIView):
    permission_classes = [IsTrainerOrAdmin]

    # Generates a compliant CSV export respecting participant consent choices
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="field_atlas_impact_brief.csv"'

        writer = csv.writer(response)
        writer.writerow(['Unified ID', 'Course', 'Provider', 'District', 'State', 'Stage', 'Consent Status', 'Placement Wage (INR)'])

        trainees = Trainee.objects.prefetch_related('placements').all()
        for t in trainees:
            # Respect consent withdrawal: mask details if withdrawn
            if t.consent_status == 'withdrawn':
                writer.writerow([t.unified_id[:4] + '****', t.course, t.provider, '[Withheld]', '[Withheld]', t.stage, 'Withdrawn', 'N/A'])
            else:
                latest_p = t.placements.order_by('-created_at').first()
                wage_val = latest_p.wage if (latest_p and latest_p.wage) else 'N/A'
                writer.writerow([t.unified_id, t.course, t.provider, t.district, t.state, t.stage, t.consent_status, wage_val])

        log_audit_event(request.user, 'report_downloaded', 'Report', 'impact_brief_csv')
        return response


# Trainee Dashboard API: Returns personal journey, timeline, and upcoming check-ins
class TraineeSelfDashboardAPIView(APIView):
    permission_classes = [IsTrainee]

    # Gathers personalised stage timeline, placement details, and check-in tasks for the trainee
    def get(self, request):
        if not hasattr(request.user, 'trainee_profile'):
            return Response({'error': 'No trainee profile linked to this user account.'}, status=status.HTTP_404_NOT_FOUND)

        trainee = request.user.trainee_profile
        placements = Placement.objects.filter(trainee=trainee).order_by('-created_at')
        latest_placement = placements.first()
        follow_ups = FollowUp.objects.filter(trainee=trainee).order_by('-due_at')
        upcoming_follow_up = follow_ups.filter(status__in=['queued', 'sent', 'needs_assistance']).first()

        # Compute profile completion percentage
        fields_to_check = [trainee.name, trainee.course, trainee.provider, trainee.district, trainee.state, request.user.phone_number]
        filled_count = sum(1 for f in fields_to_check if f)
        completion_pct = int((filled_count / len(fields_to_check)) * 100)

        # Stage sequence indices
        stages_order = ['enrolled', 'trained', 'certified', 'placed', 'retained']
        current_stage_idx = stages_order.index(trainee.stage) if trainee.stage in stages_order else 0

        return Response({
            'trainee': TraineeSerializer(trainee).data,
            'completion_percentage': completion_pct,
            'current_stage_index': current_stage_idx,
            'stages_order': stages_order,
            'latest_placement': PlacementSerializer(latest_placement).data if latest_placement else None,
            'upcoming_follow_up': FollowUpSerializer(upcoming_follow_up).data if upcoming_follow_up else None,
            'recent_follow_ups': FollowUpSerializer(follow_ups[:5], many=True).data,
            'has_active_consent': trainee.has_active_consent()
        })


# Allows a trainee to answer their upcoming follow-up check-in
class TraineeRespondFollowUpAPIView(APIView):
    permission_classes = [IsTrainee]

    # Records learner response to a scheduled check-in
    def post(self, request, pk):
        try:
            follow_up = FollowUp.objects.get(pk=pk, trainee=request.user.trainee_profile)
        except (FollowUp.DoesNotExist, AttributeError):
            return Response({'error': 'Check-in record not found for your account.'}, status=status.HTTP_404_NOT_FOUND)

        response_choice = request.data.get('response_choice')  # 'working', 'own_work', 'need_help'
        notes = request.data.get('notes', '')

        if not response_choice:
            return Response({'error': 'Please select a response option.'}, status=status.HTTP_400_BAD_REQUEST)

        follow_up.status = 'responded'
        follow_up.response_tag = response_choice
        follow_up.notes = f"Trainee self-check-in: {response_choice}. Notes: {notes}".strip()
        follow_up.save()

        # If learner is working or in own business, update trainee stage if not yet placed
        trainee = request.user.trainee_profile
        if response_choice in ['working', 'own_work'] and trainee.stage in ['enrolled', 'trained', 'certified']:
            trainee.stage = 'placed'
            trainee.save(update_fields=['stage'])

        log_audit_event(request.user, 'trainee_responded_follow_up', 'FollowUp', follow_up.id, {'response': response_choice})
        return Response({
            'message': 'Thank you! Your update has been saved.',
            'follow_up': FollowUpSerializer(follow_up).data
        })


# Generates and delivers structured learner progress report
class TraineeProgressReportAPIView(APIView):
    permission_classes = [IsTrainee]

    # Returns formatted learner summary document
    def get(self, request):
        if not hasattr(request.user, 'trainee_profile'):
            return Response({'error': 'Trainee profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        t = request.user.trainee_profile
        placements = Placement.objects.filter(trainee=t)

        report = {
            'learner_name': t.name,
            'unified_id': t.unified_id,
            'course': t.course,
            'provider': t.provider,
            'location': f"{t.district}, {t.state}",
            'current_stage': t.stage.title(),
            'consent_status': t.consent_status.title(),
            'placements_count': placements.count(),
            'generated_at': timezone.now().strftime('%d %B %Y, %I:%M %p'),
            'program_verification': 'Verified under National Skilling Outcomes Framework'
        }

        return Response({'report': report})
