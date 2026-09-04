from django.urls import path
from . import views_pages, views_api

urlpatterns = [
    # Page Routes
    path('', views_pages.index_view, name='index_view'),
    path('login/', views_pages.login_page, name='login_page'),
    path('register/', views_pages.register_page, name='register_page'),
    path('verify-otp/', views_pages.verify_otp_page, name='verify_otp_page'),
    path('forgot-password/', views_pages.forgot_password_page, name='forgot_password_page'),
    path('trainer/', views_pages.trainer_dashboard_page, name='trainer_dashboard'),
    path('trainee/', views_pages.trainee_dashboard_page, name='trainee_dashboard'),
    path('profile/', views_pages.profile_page, name='profile_page'),

    # REST APIs: Authentication
    path('api/auth/register/', views_api.RegisterAPIView.as_view(), name='api_register'),
    path('api/auth/login/', views_api.LoginAPIView.as_view(), name='api_login'),
    path('api/auth/logout/', views_api.LogoutAPIView.as_view(), name='api_logout'),
    path('api/auth/send-otp/', views_api.SendOTPAPIView.as_view(), name='api_send_otp'),
    path('api/auth/verify-otp/', views_api.VerifyOTPAPIView.as_view(), name='api_verify_otp'),
    path('api/auth/password-reset/', views_api.PasswordResetAPIView.as_view(), name='api_password_reset'),
    path('api/auth/change-password/', views_api.ChangePasswordAPIView.as_view(), name='api_change_password'),
    path('api/auth/me/', views_api.CurrentUserAPIView.as_view(), name='api_current_user'),

    # REST APIs: Profile & Localization
    path('api/profile/', views_api.ProfileAPIView.as_view(), name='api_profile'),
    path('api/profile/photo/', views_api.ProfilePhotoUploadAPIView.as_view(), name='api_profile_photo'),
    path('api/i18n/languages/', views_api.LanguageListAPIView.as_view(), name='api_languages'),
    path('api/i18n/set-language/', views_api.SetLanguageAPIView.as_view(), name='api_set_language'),

    # REST APIs: Trainer & Outcomes Management
    path('api/trainer/dashboard/', views_api.TrainerDashboardAPIView.as_view(), name='api_trainer_dashboard'),
    path('api/outcomes/trainees/', views_api.TraineeListCreateAPIView.as_view(), name='api_trainees_list_create'),
    path('api/outcomes/trainees/<int:pk>/', views_api.TraineeDetailAPIView.as_view(), name='api_trainee_detail'),
    path('api/outcomes/trainees/seed-demo/', views_api.SeedDemoTraineesAPIView.as_view(), name='api_seed_trainees'),
    path('api/outcomes/follow-ups/', views_api.FollowUpListCreateAPIView.as_view(), name='api_follow_ups_list_create'),
    path('api/outcomes/follow-ups/seed-demo/', views_api.SeedDemoFollowUpsAPIView.as_view(), name='api_seed_follow_ups'),
    path('api/outcomes/follow-ups/<int:pk>/send/', views_api.SendFollowUpAPIView.as_view(), name='api_send_follow_up'),
    path('api/outcomes/placements/', views_api.PlacementListCreateAPIView.as_view(), name='api_placements_list_create'),
    path('api/outcomes/consents/', views_api.RecordConsentAPIView.as_view(), name='api_record_consent'),
    path('api/reports/provider-export/', views_api.ProviderReportExportAPIView.as_view(), name='api_provider_export'),
    path('api/reports/impact-export/', views_api.ImpactReportExportAPIView.as_view(), name='api_impact_export'),

    # REST APIs: Trainee Self-Service
    path('api/trainee/me/dashboard/', views_api.TraineeSelfDashboardAPIView.as_view(), name='api_trainee_self_dashboard'),
    path('api/trainee/me/profile/', views_api.ProfileAPIView.as_view(), name='api_trainee_self_profile'),
    path('api/trainee/me/follow-ups/<int:pk>/respond/', views_api.TraineeRespondFollowUpAPIView.as_view(), name='api_trainee_respond_follow_up'),
    path('api/trainee/me/progress-report/', views_api.TraineeProgressReportAPIView.as_view(), name='api_trainee_progress_report'),
    path('api/trainee/me/consent/', views_api.RecordConsentAPIView.as_view(), name='api_trainee_consent'),
]
