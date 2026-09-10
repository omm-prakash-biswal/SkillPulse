from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from outcomes.models import CustomUser, Trainee, Course, TrainerCourseFeedback
from outcomes.utils import seed_default_demo_data

class FeedbackAndI18nTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        seed_default_demo_data()
        self.trainer = CustomUser.objects.filter(role='trainer').first()
        self.trainee_user = CustomUser.objects.filter(role='trainee').first()
        self.trainee_profile = Trainee.objects.first()
        self.course = Course.objects.first()

    def test_language_list_includes_odia(self):
        res = self.client.get('/api/i18n/languages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        codes = [l['code'] for l in res.data.get('languages', [])]
        self.assertIn('or', codes)
        self.assertIn('hi', codes)
        self.assertIn('en', codes)

    def test_set_language_odia(self):
        res = self.client.post('/api/i18n/set-language/', {'language': 'or'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_trainer_feedback_analytics_api(self):
        res = self.client.get('/api/feedback/trainer/analytics/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('overall_rating', res.data)
        self.assertIn('criteria', res.data)
        self.assertIn('behavior', res.data['criteria'])
        self.assertIn('classes', res.data['criteria'])
        self.assertIn('doubt_clearing', res.data['criteria'])
        self.assertIn('top_course', res.data)
        self.assertIn('needs_attention_course', res.data)
        self.assertIn('why_diagnostics', res.data['needs_attention_course'])

    def test_trainee_my_feedback_api(self):
        res = self.client.get('/api/feedback/trainee/my-feedback/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('eligible_courses', res.data)
        self.assertIn('submitted_history', res.data)

    def test_feedback_submit_api(self):
        payload = {
            'trainee_id': self.trainee_profile.id,
            'trainer_id': self.trainer.id,
            'course_id': self.course.id,
            'trainer_behavior_rating': 5,
            'trainer_teaching_rating': 4,
            'trainer_doubt_clearing_rating': 5,
            'course_practical_rating': 4,
            'course_content_rating': 5,
            'feedback_tags': ['🗣️ Clear Explanations', '🧘 Very Patient'],
            'opinion_text': 'Great course and very respectful teacher.',
            'would_recommend': True
        }
        res = self.client.post('/api/feedback/submit/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data.get('success'))
        self.assertEqual(res.data.get('overall_score'), 4.6)
        self.assertEqual(TrainerCourseFeedback.objects.count(), 1)
