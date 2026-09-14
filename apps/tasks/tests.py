from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task

User = get_user_model()


class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="clerk1", password="pass12345")

    def test_task_is_overdue_when_past_due_and_open(self):
        task = Task.objects.create(
            title="Overdue task",
            assignee=self.user,
            created_by=self.user,
            due_date=timezone.localdate() - timedelta(days=1),
            status=Task.STATUS_OPEN,
        )
        self.assertTrue(task.is_overdue)

    def test_task_not_overdue_when_completed(self):
        task = Task.objects.create(
            title="Done task",
            assignee=self.user,
            created_by=self.user,
            due_date=timezone.localdate() - timedelta(days=1),
            status=Task.STATUS_COMPLETED,
        )
        self.assertFalse(task.is_overdue)

    def test_task_not_overdue_when_due_date_in_future(self):
        task = Task.objects.create(
            title="Future task",
            assignee=self.user,
            created_by=self.user,
            due_date=timezone.localdate() + timedelta(days=5),
            status=Task.STATUS_OPEN,
        )
        self.assertFalse(task.is_overdue)


class TaskPermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="clerk1", password="pass12345")
        self.client.login(username="clerk1", password="pass12345")
        self.task = Task.objects.create(
            title="Sample",
            assignee=self.user,
            created_by=self.user,
            due_date=timezone.localdate(),
        )

    def test_delete_requires_permission(self):
        response = self.client.post(
            reverse("tasks:task_delete", args=[self.task.pk])
        )
        self.assertEqual(response.status_code, 403)