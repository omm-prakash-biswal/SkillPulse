from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from outcomes.models import CustomUser, Trainee, TraineeConsent, Placement, FollowUp, EmailOTP
from outcomes.utils import send_email_otp, verify_email_otp, seed_default_demo_data

# Comprehensive test suite covering authentication, permissions, APIs, and business rules
class FieldAtlasAPITests(TestCase):

    # Sets up base test fixtures including demo trainer, trainee, and clients
    def setUp(self):
        self.client = APIClient()

        # Seed initial demo data
        seed_default_demo_data()

        self.trainer_user = CustomUser.objects.get(email='trainer@fieldatlas.in')
        self.trainee_user = CustomUser.objects.get(email='trainee@fieldatlas.in')
        self.admin_user = CustomUser.objects.get(email='admin@fieldatlas.in')

        self.trainee_profile = Trainee.objects.get(unified_id='FA-24-0182')

    # Tests user registration with role selection and disallows self-registration as admin
    def test_registration_and_role_redirect(self):
        # 1. Successful trainer registration
        payload = {
            'full_name': 'New Trainer',
            'email': 'newtrainer@example.com',
            'password': 'SecurePassword123!',
            'role': 'trainer',
            'provider': 'Saksham',
            'district': 'Pune'
        }
        res = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['redirect_url'], '/trainer/')

        # 2. Prevent self-registration as admin
        admin_payload = {
            'full_name': 'Malicious Admin',
            'email': 'badadmin@example.com',
            'password': 'SecurePassword123!',
            'role': 'admin'
        }
        admin_res = self.client.post('/api/auth/register/', admin_payload, format='json')
        self.assertEqual(admin_res.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests 6-digit email OTP generation, verification, and expiration rules
    def test_email_otp_validation(self):
        email = 'test_otp@example.com'
        otp_obj = send_email_otp(email, purpose='registration')
        self.assertEqual(len(otp_obj.otp_code), 6)

        # Correct code verifies successfully
        valid, msg = verify_email_otp(email, otp_obj.otp_code, purpose='registration')
        self.assertTrue(valid)

        # Re-using code fails
        valid2, msg2 = verify_email_otp(email, otp_obj.otp_code, purpose='registration')
        self.assertFalse(valid2)

        # Expired code fails
        expired_otp = send_email_otp('expired@example.com', purpose='registration')
        expired_otp.expires_at = timezone.now() - timedelta(minutes=1)
        expired_otp.save()
        valid_exp, _ = verify_email_otp('expired@example.com', expired_otp.otp_code, purpose='registration')
        self.assertFalse(valid_exp)

    # Tests authenticated profile viewing and updating via REST API
    def test_profile_update(self):
        self.client.force_authenticate(user=self.trainer_user)
        res = self.client.patch('/api/profile/', {
            'full_name': 'Vikram Shinde Updated',
            'district': 'Mumbai'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.trainer_user.refresh_from_db()
        self.assertEqual(self.trainer_user.full_name, 'Vikram Shinde Updated')
        self.assertEqual(self.trainer_user.district, 'Mumbai')

    # Tests that trainees are strictly forbidden from accessing trainer management endpoints
    def test_trainee_permissions(self):
        self.client.force_authenticate(user=self.trainee_user)
        # Trainee attempting to access trainer overview dashboard
        res = self.client.get('/api/trainer/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Trainee attempting to view full trainee directory
        res_dir = self.client.get('/api/outcomes/trainees/')
        self.assertEqual(res_dir.status_code, status.HTTP_403_FORBIDDEN)

    # Tests that trainers can access overview statistics and manage outcomes
    def test_trainer_permissions(self):
        self.client.force_authenticate(user=self.trainer_user)
        res = self.client.get('/api/trainer/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', res.data)
        self.assertIn('wage_chart', res.data)

    # Tests creating a new trainee record and verifies automatic consent creation
    def test_trainee_creation(self):
        self.client.force_authenticate(user=self.trainer_user)
        payload = {
            'unified_id': 'FA-24-9999',
            'name': 'Kavita Sharma',
            'course': 'Graphic Design',
            'provider': 'Saksham',
            'district': 'Pune',
            'state': 'Maharashtra',
            'gender': 'female',
            'age_band': '18-24',
            'stage': 'enrolled',
            'consent_status': 'active'
        }
        res = self.client.post('/api/outcomes/trainees/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Trainee.objects.filter(unified_id='FA-24-9999').exists())
        self.assertTrue(TraineeConsent.objects.filter(trainee__unified_id='FA-24-9999').exists())

    # Tests that running seed demo data multiple times is completely idempotent
    def test_idempotent_demo_seeding(self):
        count_before = Trainee.objects.count()
        seed_default_demo_data()
        count_after = Trainee.objects.count()
        self.assertEqual(count_before, count_after)

    # Tests recording consent updates (grant and withdraw)
    def test_consent_recording(self):
        self.client.force_authenticate(user=self.trainer_user)
        res = self.client.post('/api/outcomes/consents/', {
            'trainee_id': self.trainee_profile.id,
            'status': 'withdrawn'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.trainee_profile.refresh_from_db()
        self.assertEqual(self.trainee_profile.consent_status, 'withdrawn')

    # Tests follow-up send behavior, verifying attempt increments and consent checks
    def test_follow_up_send_behavior(self):
        self.client.force_authenticate(user=self.trainer_user)
        follow_up = FollowUp.objects.filter(trainee=self.trainee_profile).first()
        initial_attempts = follow_up.attempts

        # 1. Sending with active consent succeeds
        res = self.client.post(f'/api/outcomes/follow-ups/{follow_up.id}/send/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        follow_up.refresh_from_db()
        self.assertEqual(follow_up.attempts, initial_attempts + 1)
        self.assertEqual(follow_up.status, 'sent')
        self.assertIsNotNone(follow_up.last_attempt_at)

        # 2. Sending when consent is withdrawn is blocked
        self.trainee_profile.consent_status = 'withdrawn'
        self.trainee_profile.save()
        res_blocked = self.client.post(f'/api/outcomes/follow-ups/{follow_up.id}/send/')
        self.assertEqual(res_blocked.status_code, status.HTTP_403_FORBIDDEN)

    # Tests trainee responding to upcoming check-in
    def test_follow_up_response_behavior(self):
        self.client.force_authenticate(user=self.trainee_user)
        follow_up = FollowUp.objects.filter(trainee=self.trainee_profile).first()
        res = self.client.post(f'/api/trainee/me/follow-ups/{follow_up.id}/respond/', {
            'response_choice': 'working',
            'notes': 'Continuing as junior technician'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        follow_up.refresh_from_db()
        self.assertEqual(follow_up.status, 'responded')
        self.assertEqual(follow_up.response_tag, 'working')

    # Tests placement retrieval and trainee-id filtering
    def test_placement_filtering(self):
        self.client.force_authenticate(user=self.trainer_user)
        res = self.client.get(f'/api/outcomes/placements/?trainee_id={self.trainee_profile.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data['placements']), 1)
        self.assertEqual(res.data['placements'][0]['trainee'], self.trainee_profile.id)
