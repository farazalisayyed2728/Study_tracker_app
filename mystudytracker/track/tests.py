import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse

from .forms import DailyLogForm, StudyGoalForm
from .models import DailyLog, StudyGoal


class StudyGoalFormTests(TestCase):
    def test_end_date_cannot_precede_start_date(self):
        form = StudyGoalForm(data={
            'title': 'Learn Django',
            'start_date': '2026-05-02',
            'end_date': '2026-05-01',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('end_date', form.errors)


class DailyLogFormTests(TestCase):
    def test_a_session_cannot_be_studied_and_a_rest_day(self):
        form = DailyLogForm(data={
            'morning_done': 'on',
            'morning_not_studied': 'on',
            'morning_hours': '1.0',
            'evening_hours': '0.0',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('morning_not_studied', form.errors)


class ToggleLogStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='faraz', password='test-password')
        self.goal = StudyGoal.objects.create(
            user=self.user,
            title='Learn Django',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )
        self.log = DailyLog.objects.create(
            goal=self.goal,
            date=date.today(),
            morning_done=True,
        )
        self.client.force_login(self.user)
        self.url = reverse('toggle_log_status', args=[self.log.id])

    def test_marking_rest_day_clears_studied_status(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'field': 'morning_not_studied', 'value': True}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.log.refresh_from_db()
        self.assertTrue(self.log.morning_not_studied)
        self.assertFalse(self.log.morning_done)

    def test_toggle_rejects_non_boolean_values(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'field': 'morning_done', 'value': 'false'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_toggle_rejects_non_object_json(self):
        response = self.client.post(
            self.url,
            data=json.dumps(['morning_done', True]),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

class TemplateCompilationTests(TestCase):
    def test_workspace_templates_compile(self):
        for template_name in (
            'track/base.html',
            'track/dashboard.html',
            'track/goal_detail.html',
            'track/create_goal.html',
            'registration/login.html',
        ):
            with self.subTest(template=template_name):
                self.assertIsNotNone(get_template(template_name))
