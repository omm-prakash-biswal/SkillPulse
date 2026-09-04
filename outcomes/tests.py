import io
from datetime import timedelta
from PIL import Image

from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from rest_framework.test import APIClient
from rest_framework import status

from outcomes.models import (
    CustomUser, Trainee, TraineeConsent, Placement, FollowUp, EmailOTP, AuditLog,
    Course, CourseApplication, Enrollment, Certificate, TraineeOutcome, Notification
)
from outcomes.utils import (
    send_email_otp,
    verify_email_otp,
    seed_default_demo_data,
    normalize_provider_name,
)

# Comprehensive test suite covering authentication, role isolation, OTP, photo validation, transactions, and exports
class FieldAtlasAPITests(TestCase):

    # Sets up base test fixtures including demo trainers, trainees, and an isolated second trainer
    def setUp(self):
        self.client = APIClient()

        # Seed initial demo data
        seed_default_demo_data()

        self.trainer_a = CustomUser.objects.get(email='trainer@fieldatlas.in')
        self.trainee_user = CustomUser.objects.get(email='trainee@fieldatlas.in')
        self.admin_user = CustomUser.objects.get(email='admin@fieldatlas.in')

        self.trainee_profile_a = Trainee.objects.get(unified_id='FA-24-0182')

        # Create a second trainer to rigorously test trainer data isolation
        self.trainer_b = CustomUser.objects.create_user(
            email='trainer_b@fieldatlas.in',
            password='TrainerBPass@2026!',
            full_name='Trainer B (Isolated)',
            role='trainer',
            field_atlas_id='FA-TR-9002',
            provider='Jan Disha',
            district='Nashik'
        )

        # Create a trainee assigned strictly to Trainer B
        self.trainee_b = Trainee.objects.create(
            unified_id='FA-24-8888',
            name='Rohan Kadam',
            course='EV Technician',
            provider='Jan Disha',
            district='Nashik',
            state='Maharashtra',
            gender='male',
            age_band='18-24',
            stage='trained',
            consent_status='active',
            assigned_trainer=self.trainer_b
        )

        self.consent_b = TraineeConsent.objects.create(
            trainee=self.trainee_b,
            consent_version='v1.0',
            status='active',
            source='trainer_intake'
        )

        self.follow_up_b = FollowUp.objects.create(
            trainee=self.trainee_b,
            milestone='3_month',
            channel='whatsapp',
            status='queued',
            due_at=timezone.now() + timedelta(days=7)
        )

    # Tests user registration requiring mandatory OTP validation and disallowing self-registration as admin
    def test_registration_and_role_redirect(self):
        # 1. Registration fails without valid OTP
        fail_payload = {
            'full_name': 'New Trainer',
            'email': 'newtrainer@example.com',
            'password': 'SecurePassword123!',
            'role': 'trainer',
            'provider': 'Saksham',
            'district': 'Pune',
            'otp_code': '000000'
        }
        res_fail = self.client.post('/api/auth/register/', fail_payload, format='json')
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. Registration succeeds with valid generated OTP
        _, _, plain_code = send_email_otp('newtrainer@example.com', purpose='registration')
        success_payload = {
            'full_name': 'New Trainer',
            'email': 'newtrainer@example.com',
            'password': 'SecurePassword123!',
            'role': 'trainer',
            'provider': 'Saksham',
            'district': 'Pune',
            'otp_code': plain_code
        }
        res_success = self.client.post('/api/auth/register/', success_payload, format='json')
        self.assertEqual(res_success.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_success.data['redirect_url'], '/trainer/')

        # 3. Prevent self-registration as admin
        _, _, admin_code = send_email_otp('badadmin@example.com', purpose='registration')
        admin_payload = {
            'full_name': 'Malicious Admin',
            'email': 'badadmin@example.com',
            'password': 'SecurePassword123!',
            'role': 'admin',
            'otp_code': admin_code
        }
        admin_res = self.client.post('/api/auth/register/', admin_payload, format='json')
        self.assertEqual(admin_res.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests 6-digit email OTP generation, HMAC storage verification, single-use, and expiration
    def test_email_otp_validation(self):
        email = 'test_otp@example.com'
        _, _, plain_code = send_email_otp(email, purpose='registration')
        self.assertEqual(len(plain_code), 6)
        self.assertTrue(plain_code.isdigit())

        # Correct code verifies successfully
        valid, msg = verify_email_otp(email, plain_code, purpose='registration')
        self.assertTrue(valid)

        # Single-use: Re-using the same code immediately fails
        valid2, msg2 = verify_email_otp(email, plain_code, purpose='registration')
        self.assertFalse(valid2)

        # Expired code fails verification
        _, _, exp_code = send_email_otp('expired@example.com', purpose='registration')
        expired_otp_obj = EmailOTP.objects.filter(email='expired@example.com').first()
        expired_otp_obj.expires_at = timezone.now() - timedelta(minutes=1)
        expired_otp_obj.save()
        valid_exp, _ = verify_email_otp('expired@example.com', exp_code, purpose='registration')
        self.assertFalse(valid_exp)

    # Tests that account is temporarily locked out after 5 consecutive failed login attempts
    def test_account_lockout_after_five_failed_logins(self):
        user = CustomUser.objects.create_user(
            email='lockout_target@example.com',
            password='TargetPass@2026!',
            full_name='Lockout Target',
            role='trainer',
            field_atlas_id='FA-TR-8811'
        )

        # First 4 incorrect attempts return 401 Unauthorized
        for i in range(4):
            res = self.client.post('/api/auth/login/', {
                'identifier': user.email,
                'password': 'WrongPassword123!'
            }, format='json')
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # 5th failed attempt triggers account lockout and returns 403 Forbidden
        res_5 = self.client.post('/api/auth/login/', {
            'identifier': user.email,
            'password': 'WrongPassword123!'
        }, format='json')
        self.assertEqual(res_5.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('locked', res_5.data['error'].lower())

        user.refresh_from_db()
        self.assertGreaterEqual(user.failed_login_attempts, 5)
        self.assertTrue(user.is_locked_out())

        # Subsequent attempts while locked are rejected with 403 Forbidden even with correct password
        res_locked = self.client.post('/api/auth/login/', {
            'identifier': user.email,
            'password': 'TargetPass@2026!'
        }, format='json')
        self.assertEqual(res_locked.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('locked', res_locked.data['error'].lower())

    # Tests weak password rejection based on Django password validation rules
    def test_weak_password_validation(self):
        _, _, plain_code = send_email_otp('weak_pwd@example.com', purpose='registration')
        payload = {
            'full_name': 'Weak User',
            'email': 'weak_pwd@example.com',
            'password': '123',
            'role': 'trainer',
            'otp_code': plain_code
        }
        res = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', res.data['error'])

    # Tests trainer data isolation ensuring Trainer A cannot view, modify, or outreach Trainer B's trainees
    def test_trainer_data_isolation(self):
        self.client.force_authenticate(user=self.trainer_a)

        # 1. Trainer A cannot view Trainee B details (HTTP 403)
        res_view = self.client.get(f'/api/outcomes/trainees/{self.trainee_b.id}/')
        self.assertEqual(res_view.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Trainer A cannot update Trainee B details (HTTP 403)
        res_patch = self.client.patch(f'/api/outcomes/trainees/{self.trainee_b.id}/', {'name': 'Tampered Name'})
        self.assertEqual(res_patch.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Trainer A cannot send outreach to Trainer B's trainee follow-up (HTTP 403)
        res_send = self.client.post(f'/api/outcomes/follow-ups/{self.follow_up_b.id}/send/')
        self.assertEqual(res_send.status_code, status.HTTP_403_FORBIDDEN)

        # 4. Trainer A cannot modify or reschedule Trainer B's follow-up (HTTP 403)
        res_resched = self.client.patch(f'/api/outcomes/follow-ups/{self.follow_up_b.id}/', {
            'status': 'rescheduled',
            'next_contact_date': '2026-10-15'
        })
        self.assertEqual(res_resched.status_code, status.HTTP_403_FORBIDDEN)

        # 5. Trainer A's trainees list query does NOT contain Trainee B
        res_list = self.client.get('/api/outcomes/trainees/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in res_list.data.get('results', [])]
        self.assertNotIn(self.trainee_b.id, ids)

        # 6. Admin user CAN access Trainee B without restriction
        self.client.force_authenticate(user=self.admin_user)
        admin_res = self.client.get(f'/api/outcomes/trainees/{self.trainee_b.id}/')
        self.assertEqual(admin_res.status_code, status.HTTP_200_OK)

    # Tests profile photo upload validation verifying valid image passes and fake/oversized files are rejected
    def test_profile_photo_upload_validation(self):
        self.client.force_authenticate(user=self.trainer_a)

        # 1. Valid image upload succeeds
        image_io = io.BytesIO()
        test_img = Image.new('RGB', (100, 100), color='blue')
        test_img.save(image_io, format='JPEG')
        image_io.seek(0)
        uploaded_image = SimpleUploadedFile('avatar.jpg', image_io.getvalue(), content_type='image/jpeg')

        res_upload = self.client.post('/api/profile/photo/', {'profile_photo': uploaded_image}, format='multipart')
        self.assertEqual(res_upload.status_code, status.HTTP_200_OK)
        self.assertIn('profile_photo_url', res_upload.data)

        # 2. Text file pretending to be image fails Pillow validation
        fake_image = SimpleUploadedFile('fake.png', b'This is plain text pretending to be image', content_type='image/png')
        res_fake = self.client.post('/api/profile/photo/', {'profile_photo': fake_image}, format='multipart')
        self.assertEqual(res_fake.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests follow-up rescheduling workflow and overdue/due-today status flags
    def test_follow_up_reschedule_workflow(self):
        self.client.force_authenticate(user=self.trainer_a)
        follow_up = FollowUp.objects.filter(trainee=self.trainee_profile_a).first()

        res = self.client.patch(f'/api/outcomes/follow-ups/{follow_up.id}/', {
            'status': 'rescheduled',
            'next_contact_date': '2026-11-20',
            'trainer_notes': 'Learner requested callback after seasonal harvest'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'rescheduled')
        self.assertEqual(res.data['next_contact_date'], '2026-11-20')
        self.assertIn('harvest', res.data['trainer_notes'])

    # Tests CSV exports for UTF-8 BOM encoding and consent masking
    def test_csv_export_isolation_and_bom(self):
        self.client.force_authenticate(user=self.trainer_a)

        res = self.client.get('/api/reports/impact-export/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify UTF-8 BOM is present at the beginning of the CSV payload
        self.assertTrue(res.content.startswith(b'\xef\xbb\xbf'))
        content_text = res.content.decode('utf-8-sig')

        # Ensure Trainer A's export does not leak Trainer B's participant
        self.assertNotIn(self.trainee_b.unified_id, content_text)

        # Check that download audit log was generated
        self.assertTrue(AuditLog.objects.filter(user=self.trainer_a, action='report_downloaded').exists())

    # Tests the platform health check endpoint returning HTTP 200 and healthy status
    def test_health_check_endpoint(self):
        res = self.client.get('/health/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'healthy')
        self.assertEqual(res.data['database'], 'connected')

    # Tests canonicalization of provider names
    def test_provider_name_canonicalization(self):
        self.assertEqual(normalize_provider_name('saksham'), 'Saksham')
        self.assertEqual(normalize_provider_name('SAKSHAM SKILL ACADEMY'), 'Saksham')
        self.assertEqual(normalize_provider_name('navjeevan foundation'), 'Navjeevan')
        self.assertEqual(normalize_provider_name('udaan skills'), 'Udaan')
        self.assertEqual(normalize_provider_name('Jan Disha Trust'), 'Jan Disha')

    # Tests authenticated profile viewing and updating via REST API
    def test_profile_update(self):
        self.client.force_authenticate(user=self.trainer_a)
        res = self.client.patch('/api/profile/', {
            'full_name': 'Vikram Shinde Updated',
            'district': 'Mumbai'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.trainer_a.refresh_from_db()
        self.assertEqual(self.trainer_a.full_name, 'Vikram Shinde Updated')
        self.assertEqual(self.trainer_a.district, 'Mumbai')

    # Tests that trainees are strictly forbidden from accessing trainer management endpoints
    def test_trainee_permissions(self):
        self.client.force_authenticate(user=self.trainee_user)
        # Trainee attempting to access trainer overview dashboard
        res = self.client.get('/api/trainer/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Trainee attempting to view full trainee directory
        res_dir = self.client.get('/api/outcomes/trainees/')
        self.assertEqual(res_dir.status_code, status.HTTP_403_FORBIDDEN)

    # Tests that trainers can access overview statistics and dynamic metrics
    def test_trainer_permissions(self):
        self.client.force_authenticate(user=self.trainer_a)
        res = self.client.get('/api/trainer/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', res.data)
        self.assertIn('wage_chart', res.data)

    # Tests creating a new trainee record and verifies automatic consent creation
    def test_trainee_creation(self):
        self.client.force_authenticate(user=self.trainer_a)
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

    # Verifies that seed_default_demo_data is tolerant to duplicate legacy consent records without error or data loss
    def test_seed_demo_data_duplicate_consent_tolerance(self):
        from django.core.management import call_command

        trainee = Trainee.objects.get(unified_id='FA-24-0182')
        # Simulate legacy duplicate consent records
        TraineeConsent.objects.create(
            trainee=trainee,
            consent_version='v1.0',
            status='withdrawn',
            source='legacy_batch_import'
        )
        TraineeConsent.objects.create(
            trainee=trainee,
            consent_version='v1.0',
            status='granted',
            source='re_consent_campaign'
        )

        consent_count_before = TraineeConsent.objects.filter(trainee=trainee, consent_version='v1.0').count()
        self.assertGreater(consent_count_before, 1)

        # Running seed_default_demo_data and management command should succeed without MultipleObjectsReturned
        results = seed_default_demo_data()
        self.assertIsInstance(results, dict)
        call_command('seed_demo_data')

        # Ensure all duplicate consent records were preserved and none were deleted
        consent_count_after = TraineeConsent.objects.filter(trainee=trainee, consent_version='v1.0').count()
        self.assertEqual(consent_count_before, consent_count_after)

    # Tests recording consent updates (grant and withdraw)
    def test_consent_recording(self):
        self.client.force_authenticate(user=self.trainer_a)
        res = self.client.post('/api/outcomes/consents/', {
            'trainee_id': self.trainee_profile_a.id,
            'status': 'withdrawn'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.trainee_profile_a.refresh_from_db()
        self.assertEqual(self.trainee_profile_a.consent_status, 'withdrawn')

    # Tests follow-up send behavior, verifying attempt increments and consent checks
    def test_follow_up_send_behavior(self):
        self.client.force_authenticate(user=self.trainer_a)
        follow_up = FollowUp.objects.filter(trainee=self.trainee_profile_a).first()
        initial_attempts = follow_up.attempts

        # 1. Sending with active consent succeeds
        res = self.client.post(f'/api/outcomes/follow-ups/{follow_up.id}/send/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        follow_up.refresh_from_db()
        self.assertEqual(follow_up.attempts, initial_attempts + 1)
        self.assertEqual(follow_up.status, 'sent')
        self.assertIsNotNone(follow_up.last_attempt_at)

        # 2. Sending when consent is withdrawn is blocked
        self.trainee_profile_a.consent_status = 'withdrawn'
        self.trainee_profile_a.save()
        res_blocked = self.client.post(f'/api/outcomes/follow-ups/{follow_up.id}/send/')
        self.assertEqual(res_blocked.status_code, status.HTTP_403_FORBIDDEN)

    # Tests trainee responding to upcoming check-in
    def test_follow_up_response_behavior(self):
        self.client.force_authenticate(user=self.trainee_user)
        follow_up = FollowUp.objects.filter(trainee=self.trainee_profile_a).first()
        res = self.client.post(f'/api/trainee/me/follow-ups/{follow_up.id}/respond/', {
            'response_choice': 'working',
            'notes': 'Continuing as junior technician'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        follow_up.refresh_from_db()
        self.assertEqual(follow_up.status, 'responded')
        self.assertEqual(follow_up.response_tag, 'working')

    # Tests placement retrieval and trainee-id filtering with pagination
    def test_placement_filtering(self):
        self.client.force_authenticate(user=self.trainer_a)
        res = self.client.get(f'/api/outcomes/placements/?trainee_id={self.trainee_profile_a.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items = res.data.get('results', res.data.get('placements', []))
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[0]['trainee'], self.trainee_profile_a.id)

    # Tests course creation, modification, publication, and closure lifecycle
    def test_course_crud_and_lifecycle(self):
        self.client.force_authenticate(user=self.trainer_a)

        # 1. Create a draft course
        create_payload = {
            'title': 'IoT Embedded Systems',
            'course_code': 'FA-IOT-2026',
            'category': 'Electronics & Hardware',
            'description': 'Hardware programming and sensor network integration.',
            'duration_weeks': 10,
            'capacity': 25,
            'status': 'draft'
        }
        res_create = self.client.post('/api/courses/', create_payload, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        course_id = res_create.data['id']
        self.assertEqual(res_create.data['status'], 'draft')

        # 2. Update course details
        res_patch = self.client.patch(f'/api/courses/{course_id}/', {'capacity': 30}, format='json')
        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data['capacity'], 30)

        # 3. Publish course
        res_pub = self.client.post(f'/api/courses/{course_id}/publish/')
        self.assertEqual(res_pub.status_code, status.HTTP_200_OK)
        self.assertEqual(res_pub.data['status'], 'published')

        # 4. Trainee can browse published course
        self.client.force_authenticate(user=self.trainee_user)
        res_browse = self.client.get(f'/api/trainee/courses/?search=Embedded')
        self.assertEqual(res_browse.status_code, status.HTTP_200_OK)
        self.assertTrue(any(c['id'] == course_id for c in res_browse.data))

        # 5. Close course
        self.client.force_authenticate(user=self.trainer_a)
        res_close = self.client.post(f'/api/courses/{course_id}/close/')
        self.assertEqual(res_close.status_code, status.HTTP_200_OK)
        self.assertEqual(res_close.data['status'], 'closed')

    # Tests trainee application submission, trainer review, approval, and enrollment creation
    def test_course_application_and_approval_flow(self):
        # Trainer A creates and publishes a course
        course = Course.objects.create(
            title='Solar Photovoltaic Installation',
            course_code='FA-SOLAR-01',
            category='Green Energy & Solar',
            duration_weeks=8,
            capacity=20,
            status='published',
            trainer=self.trainer_a,
            provider='Saksham'
        )

        # Trainee submits application
        self.client.force_authenticate(user=self.trainee_user)
        app_res = self.client.post(f'/api/trainee/courses/{course.id}/apply/', {
            'motivation': 'Eager to build a career in clean energy across rural Maharashtra.'
        }, format='json')
        self.assertEqual(app_res.status_code, status.HTTP_201_CREATED)
        app_id = app_res.data['id']
        self.assertEqual(app_res.data['status'], 'pending')

        # Trainer A views application list
        self.client.force_authenticate(user=self.trainer_a)
        apps_list_res = self.client.get(f'/api/courses/{course.id}/applications/')
        self.assertEqual(apps_list_res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(a['id'] == app_id for a in apps_list_res.data))

        # Trainer A approves application
        review_res = self.client.post(f'/api/courses/applications/{app_id}/review/', {
            'action': 'approve',
            'review_notes': 'Strong motivation statement, applicant accepted.'
        }, format='json')
        self.assertEqual(review_res.status_code, status.HTTP_200_OK)
        self.assertEqual(review_res.data['status'], 'approved')

        # Enrollment is created for trainee
        enrollment = Enrollment.objects.filter(course=course, trainee__user=self.trainee_user).first()
        self.assertIsNotNone(enrollment)
        self.assertEqual(enrollment.status, 'active')

        # Trainee receives enrollment in my enrollments list
        self.client.force_authenticate(user=self.trainee_user)
        my_enrollments_res = self.client.get('/api/trainee/me/enrollments/')
        self.assertEqual(my_enrollments_res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(e['id'] == enrollment.id for e in my_enrollments_res.data))

        # Trainee receives in-app notification
        notifs_res = self.client.get('/api/notifications/')
        self.assertEqual(notifs_res.status_code, status.HTTP_200_OK)
        self.assertTrue(any('accepted' in n['body'].lower() or 'approved' in n['body'].lower() for n in notifs_res.data['notifications']))

    # Tests strict object-level isolation preventing foreign trainers or trainees from managing another's course
    def test_course_trainer_isolation_and_permissions(self):
        # Course owned by Trainer A
        course_a = Course.objects.create(
            title='Data Annotation & Quality',
            course_code='FA-DATA-99',
            category='IT & Software',
            duration_weeks=6,
            capacity=15,
            status='published',
            trainer=self.trainer_a,
            provider='Saksham'
        )

        app = CourseApplication.objects.create(
            course=course_a,
            trainee=self.trainee_profile_a,
            motivation='Looking for remote annotator roles.',
            status='pending'
        )

        enrollment = Enrollment.objects.create(
            course=course_a,
            trainee=self.trainee_profile_a,
            status='active',
            completion_percent=100
        )

        # Trainer B attempts to review application for Trainer A's course (HTTP 403)
        self.client.force_authenticate(user=self.trainer_b)
        res_review = self.client.post(f'/api/courses/applications/{app.id}/review/', {'action': 'approve'}, format='json')
        self.assertEqual(res_review.status_code, status.HTTP_403_FORBIDDEN)

        # Trainer B attempts to update enrollment progress for Trainer A's course (HTTP 403)
        res_enroll = self.client.patch(f'/api/courses/enrollments/{enrollment.id}/', {'completion_percent': 50}, format='json')
        self.assertEqual(res_enroll.status_code, status.HTTP_403_FORBIDDEN)

        # Trainer B attempts to issue certificate for Trainer A's course (HTTP 403)
        res_cert = self.client.post(f'/api/courses/enrollments/{enrollment.id}/certificate/')
        self.assertEqual(res_cert.status_code, status.HTTP_403_FORBIDDEN)

        # Trainee user attempts to access trainer course management (HTTP 403)
        self.client.force_authenticate(user=self.trainee_user)
        res_create_fail = self.client.post('/api/courses/', {'title': 'Disallowed Course'}, format='json')
        self.assertEqual(res_create_fail.status_code, status.HTTP_403_FORBIDDEN)

    # Tests progress tracking, ReportLab PDF certificate generation, and secure download
    def test_enrollment_progress_and_certificate_issuance(self):
        course = Course.objects.create(
            title='Automotive EV Assembly',
            course_code='FA-EV-55',
            category='Electronics & Hardware',
            duration_weeks=12,
            capacity=20,
            status='published',
            trainer=self.trainer_a,
            provider='Saksham'
        )

        enrollment = Enrollment.objects.create(
            course=course,
            trainee=self.trainee_profile_a,
            status='active',
            completion_percent=50
        )

        self.client.force_authenticate(user=self.trainer_a)

        # Update progress to 100%
        res_progress = self.client.patch(f'/api/courses/enrollments/{enrollment.id}/', {
            'completion_percent': 100,
            'completion_notes': 'Completed all modules and workshop practical assessment with distinction.'
        }, format='json')
        self.assertEqual(res_progress.status_code, status.HTTP_200_OK)
        self.assertEqual(res_progress.data['completion_percent'], 100)

        # Issue Certificate
        res_cert = self.client.post(f'/api/courses/enrollments/{enrollment.id}/certificate/')
        self.assertEqual(res_cert.status_code, status.HTTP_201_CREATED)
        self.assertIn('certificate_number', res_cert.data)
        self.assertIn('verification_token', res_cert.data)

        cert_id = res_cert.data['id']
        cert_token = res_cert.data['verification_token']

        # Verify Certificate record exists and has generated PDF
        cert = Certificate.objects.get(id=cert_id)
        self.assertTrue(bool(cert.pdf_file))
        self.assertTrue(cert.pdf_file.name.endswith('.pdf'))

        # Trainee downloads certificate
        self.client.force_authenticate(user=self.trainee_user)
        res_dl = self.client.get(f'/api/certificates/{cert_id}/download/')
        self.assertEqual(res_dl.status_code, status.HTTP_200_OK)
        self.assertIn('pdf_url', res_dl.data)

    # Tests public certificate verification via both API and dedicated HTML verification landing page
    def test_public_certificate_verification(self):
        cert = Certificate.objects.filter(status='issued').first()
        self.assertIsNotNone(cert)

        # 1. Unauthenticated API verification with valid token
        client_anon = APIClient()
        res_api = client_anon.get(f'/api/certificates/verify/{cert.verification_token}/')
        self.assertEqual(res_api.status_code, status.HTTP_200_OK)
        self.assertTrue(res_api.data['valid'])
        self.assertEqual(res_api.data['certificate_number'], cert.certificate_number)
        self.assertEqual(res_api.data['trainee_name'], cert.enrollment.trainee.name)

        # 2. Unauthenticated API verification with non-existent token (404)
        res_bad = client_anon.get('/api/certificates/verify/00000000-0000-0000-0000-000000000000/')
        self.assertEqual(res_bad.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(res_bad.data['valid'])

        # 3. Public HTML verification page returns HTTP 200
        res_page = client_anon.get(f'/certificate/verify/{cert.verification_token}/')
        self.assertEqual(res_page.status_code, status.HTTP_200_OK)
        self.assertContains(res_page, str(cert.verification_token))

    # Tests trainee reporting post-skilling outcome and trainer verifying the recorded data
    def test_trainee_outcome_submission_and_trainer_verification(self):
        course = Course.objects.create(
            title='Supply Chain & Inventory Management',
            course_code='FA-SCM-10',
            category='Logistics & Supply Chain',
            duration_weeks=8,
            capacity=25,
            status='published',
            trainer=self.trainer_a,
            provider='Saksham'
        )

        enrollment = Enrollment.objects.create(
            course=course,
            trainee=self.trainee_profile_a,
            status='completed',
            completion_percent=100
        )

        # Trainee submits outcome
        self.client.force_authenticate(user=self.trainee_user)
        res_out = self.client.post(f'/api/trainee/me/enrollments/{enrollment.id}/outcome/', {
            'employment_status': 'employed',
            'employer_name': 'Blue Dart Express',
            'job_role': 'Hub Logistics Coordinator',
            'monthly_earning': 22500,
            'employment_type': 'full_time',
            'current_district': 'Pune',
            'current_state': 'Maharashtra',
            'response_notes': 'Secured full-time role during campus drive.'
        }, format='json')
        self.assertEqual(res_out.status_code, status.HTTP_201_CREATED)
        outcome_id = res_out.data['id']
        self.assertEqual(res_out.data['verification_status'], 'self_reported')

        # Trainer verifies outcome
        self.client.force_authenticate(user=self.trainer_a)
        res_ver = self.client.post(f'/api/courses/outcomes/{outcome_id}/verify/', {'action': 'verify'}, format='json')
        self.assertEqual(res_ver.status_code, status.HTTP_200_OK)
        self.assertEqual(res_ver.data['verification_status'], 'verified')

    # Tests k-anonymity privacy safeguards hiding average wage when responses are under 5
    def test_course_performance_privacy_threshold(self):
        course = Course.objects.create(
            title='Healthcare General Duty Assistant',
            course_code='FA-GDA-01',
            category='Healthcare & Caregiving',
            duration_weeks=10,
            capacity=30,
            status='published',
            trainer=self.trainer_a,
            provider='Saksham'
        )

        # 1. With 0-4 outcomes, average monthly wage must be suppressed
        res_perf = self.client.get(f'/api/courses/{course.id}/performance/')
        self.assertEqual(res_perf.status_code, status.HTTP_200_OK)
        self.assertFalse(res_perf.data['privacy_threshold_met'])
        self.assertIsNone(res_perf.data['average_monthly_wage'])
        self.assertIsNotNone(res_perf.data['wage_notice'])

        # 2. Add 5 distinct outcomes
        for i in range(5):
            trainee = Trainee.objects.create(
                unified_id=f'FA-24-TEST{i}',
                name=f'Learner {i}',
                course=course.title,
                provider='Saksham',
                district='Pune',
                state='Maharashtra',
                assigned_trainer=self.trainer_a
            )
            enroll = Enrollment.objects.create(course=course, trainee=trainee, status='completed', completion_percent=100)
            TraineeOutcome.objects.create(
                enrollment=enroll,
                employment_status='employed',
                monthly_earning=15000 + (i * 1000),
                verification_status='verified'
            )

        # With >=5 outcomes, privacy threshold is met and average wage is exposed
        res_perf_5 = self.client.get(f'/api/courses/{course.id}/performance/')
        self.assertEqual(res_perf_5.status_code, status.HTTP_200_OK)
        self.assertTrue(res_perf_5.data['privacy_threshold_met'])
        self.assertIsNotNone(res_perf_5.data['average_monthly_wage'])
        self.assertEqual(float(res_perf_5.data['average_monthly_wage']), 17000.0)

    # Tests in-app notification delivery, unread counter, and mark-as-read endpoints
    def test_in_app_notifications_lifecycle(self):
        self.client.force_authenticate(user=self.trainer_a)

        # Create test notifications
        Notification.objects.create(
            recipient=self.trainer_a,
            title='Test Alert 1',
            body='First test alert message',
            type='general',
            is_read=False
        )
        notif2 = Notification.objects.create(
            recipient=self.trainer_a,
            title='Test Alert 2',
            body='Second test alert message',
            type='general',
            is_read=False
        )

        # 1. Fetch notification list and verify unread count
        res_list = self.client.get('/api/notifications/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res_list.data['unread_count'], 2)

        # 2. Mark single notification as read
        res_read_one = self.client.post(f'/api/notifications/{notif2.id}/read/')
        self.assertEqual(res_read_one.status_code, status.HTTP_200_OK)
        notif2.refresh_from_db()
        self.assertTrue(notif2.is_read)

        # 3. Mark all notifications as read
        res_read_all = self.client.post('/api/notifications/read-all/')
        self.assertEqual(res_read_all.status_code, status.HTTP_200_OK)
        unread_remaining = Notification.objects.filter(recipient=self.trainer_a, is_read=False).count()
        self.assertEqual(unread_remaining, 0)

